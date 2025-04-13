import asyncio
import json
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import aclosing, suppress
from typing import Any

from fastapi import WebSocket
from loguru import logger

from voicebot.dialog.model import DialogModel
from voicebot.dialog.sentences import split_sentences
from voicebot.stt.recognizer import RecognitionError, Recognizer
from voicebot.tts import Synthesizer

SynthesisQueue = asyncio.Queue[asyncio.Task[bytes] | None]


class VoiceSession:
    """Цикл голосового диалога для одного WebSocket-подключения.

    Слушает фразу пользователя (STT), стримит ответ LLM, озвучивает его по предложениям
    (TTS) и ждёт, пока клиент доиграет аудио, после чего снова начинает слушать.
    Пока бот говорит, входящее аудио отбрасывается, чтобы бот не распознавал сам себя.
    """

    def __init__(
        self,
        websocket: WebSocket,
        recognizer: Recognizer,
        dialog: DialogModel,
        synthesizer: Synthesizer,
        session_id: str | None = None,
        playback_timeout: float = 60.0,
        audio_queue_size: int = 256,
    ) -> None:
        self.id = session_id or uuid.uuid4().hex
        self._ws = websocket
        self._recognizer = recognizer
        self._dialog = dialog
        self._synthesizer = synthesizer
        self._playback_timeout = playback_timeout
        self._audio: asyncio.Queue[bytes] = asyncio.Queue(maxsize=audio_queue_size)
        self._listening = False
        self._playback_finished = asyncio.Event()
        self._log = logger.bind(session=self.id)

    async def run(self) -> None:
        """Работает, пока клиент не отключится."""
        await self._send({"type": "session", "id": self.id})
        reader = asyncio.create_task(self._read_client())
        conversation = asyncio.create_task(self._converse())
        try:
            done, _ = await asyncio.wait({reader, conversation}, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                task.result()
        finally:
            for task in (reader, conversation):
                task.cancel()
            await asyncio.gather(reader, conversation, return_exceptions=True)
            self._log.info("Сессия завершена")

    async def _converse(self) -> None:
        while True:
            try:
                text = await self._listen()
            except RecognitionError as exc:
                self._log.warning("Ошибка распознавания: {error}", error=exc)
                await self._send({"type": "error", "text": "Не удалось распознать речь, попробуйте ещё раз"})
                await asyncio.sleep(1)
                continue
            if not text:
                continue
            try:
                await self._answer(text)
            except Exception:
                self._log.exception("Не удалось сформировать ответ")
                await self._send({"type": "error", "text": "Не удалось получить ответ, повторите вопрос"})

    async def _read_client(self) -> None:
        while True:
            message = await self._ws.receive()
            if message["type"] == "websocket.disconnect":
                return
            if (chunk := message.get("bytes")) is not None:
                if self._listening:
                    with suppress(asyncio.QueueFull):
                        self._audio.put_nowait(chunk)
            elif (text := message.get("text")) is not None:
                self._handle_command(text)

    def _handle_command(self, raw: str) -> None:
        try:
            command = json.loads(raw)
        except json.JSONDecodeError:
            self._log.warning("Некорректная команда клиента: {raw}", raw=raw[:100])
            return
        if command.get("type") == "playback_finished":
            self._playback_finished.set()

    async def _audio_stream(self) -> AsyncIterator[bytes]:
        while True:
            yield await self._audio.get()

    async def _listen(self) -> str:
        while not self._audio.empty():
            self._audio.get_nowait()
        self._listening = True
        try:
            async with aclosing(self._recognizer.recognize(self._audio_stream())) as transcripts:
                async for transcript in transcripts:
                    if transcript.text:
                        status = "final" if transcript.final else "partial"
                        await self._send({"type": "transcription", "status": status, "text": transcript.text})
                    if transcript.final:
                        return transcript.text
        finally:
            self._listening = False
        return ""

    async def _answer(self, text: str) -> None:
        self._log.info("Пользователь: {text}", text=text)
        started = time.perf_counter()
        self._playback_finished.clear()
        pending: SynthesisQueue = asyncio.Queue()
        delivery = asyncio.create_task(self._deliver_audio(pending, started))
        sentences: list[str] = []
        try:
            async for sentence in split_sentences(self._dialog.stream_reply(self.id, text)):
                sentences.append(sentence)
                await self._send({"type": "response", "status": "partial", "text": " ".join(sentences)})
                pending.put_nowait(asyncio.create_task(self._synthesizer.synthesize(sentence)))
            pending.put_nowait(None)
            await delivery
        except BaseException:
            delivery.cancel()
            self._discard(pending)
            raise

        reply = " ".join(sentences)
        self._log.info("Бот: {reply}", reply=reply)
        await self._send({"type": "response", "status": "final", "text": reply})
        if sentences:
            with suppress(TimeoutError):
                await asyncio.wait_for(self._playback_finished.wait(), self._playback_timeout)

    async def _deliver_audio(self, pending: SynthesisQueue, started: float) -> None:
        first = True
        while (task := await pending.get()) is not None:
            await self._ws.send_bytes(await task)
            if first:
                first = False
                latency_ms = round((time.perf_counter() - started) * 1000)
                self._log.info("Первый аудиоответ через {latency} мс", latency=latency_ms)

    @staticmethod
    def _discard(pending: SynthesisQueue) -> None:
        while not pending.empty():
            task = pending.get_nowait()
            if task is None:
                continue
            task.cancel()
            if task.done() and not task.cancelled():
                task.exception()

    async def _send(self, payload: dict[str, Any]) -> None:
        await self._ws.send_text(json.dumps(payload, ensure_ascii=False))
