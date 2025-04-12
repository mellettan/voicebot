from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from typing import Protocol

import grpc
from loguru import logger

from voicebot.auth import TokenProvider
from voicebot.stt.proto import recognition_pb2 as pb
from voicebot.stt.proto.recognition_pb2_grpc import SmartSpeechStub


@dataclass(frozen=True, slots=True)
class Transcript:
    """Гипотеза распознавания: промежуточная или финальная для фразы."""

    text: str
    final: bool


class RecognitionError(RuntimeError):
    """Ошибка потокового распознавания речи."""


class Recognizer(Protocol):
    def recognize(self, audio: AsyncIterator[bytes]) -> AsyncIterator[Transcript]: ...


@dataclass(frozen=True, slots=True)
class RecognitionConfig:
    host: str
    sample_rate: int
    language: str
    no_speech_timeout_seconds: int
    max_speech_timeout_seconds: int
    hints: Sequence[str] = ()
    use_tls: bool = True


class SaluteSpeechRecognizer:
    """Потоковое распознавание SaluteSpeech по gRPC.

    Один вызов `recognize` распознаёт одну фразу: SaluteSpeech закрывает поток на конце
    высказывания (EOU), после чего генератор завершается.
    """

    def __init__(
        self,
        config: RecognitionConfig,
        tokens: TokenProvider,
        root_certificates: bytes | None = None,
    ) -> None:
        self._config = config
        self._tokens = tokens
        self._root_certificates = root_certificates

    async def recognize(self, audio: AsyncIterator[bytes]) -> AsyncIterator[Transcript]:
        """Отправляет PCM-чанки в SaluteSpeech и отдаёт гипотезы по мере поступления."""
        token = await self._tokens.get_token()
        async with self._open_channel(token) as channel:
            call = SmartSpeechStub(channel).Recognize(self._requests(audio))
            try:
                async for response in call:
                    transcript = self._parse(response)
                    if transcript is None:
                        continue
                    yield transcript
                    if transcript.final:
                        return
            except grpc.aio.AioRpcError as exc:
                raise RecognitionError(f"{exc.code().name}: {exc.details()}") from exc
            finally:
                call.cancel()

    def _open_channel(self, token: str) -> grpc.aio.Channel:
        if not self._config.use_tls:
            return grpc.aio.insecure_channel(self._config.host)
        credentials = grpc.composite_channel_credentials(
            grpc.ssl_channel_credentials(root_certificates=self._root_certificates),
            grpc.access_token_call_credentials(token),
        )
        return grpc.aio.secure_channel(self._config.host, credentials)

    async def _requests(self, audio: AsyncIterator[bytes]) -> AsyncIterator[pb.RecognitionRequest]:
        yield pb.RecognitionRequest(options=self._options())
        async for chunk in audio:
            yield pb.RecognitionRequest(audio_chunk=chunk)

    def _options(self) -> pb.RecognitionOptions:
        options = pb.RecognitionOptions(
            audio_encoding=pb.RecognitionOptions.PCM_S16LE,
            sample_rate=self._config.sample_rate,
            channels_count=1,
            language=self._config.language,
            enable_partial_results=pb.OptionalBool(enable=True),
            hints=pb.Hints(words=list(self._config.hints)),
        )
        options.no_speech_timeout.FromSeconds(self._config.no_speech_timeout_seconds)
        options.max_speech_timeout.FromSeconds(self._config.max_speech_timeout_seconds)
        return options

    @staticmethod
    def _parse(response: pb.RecognitionResponse) -> Transcript | None:
        if not response.HasField("transcription"):
            return None
        transcription = response.transcription
        if not transcription.results:
            return Transcript(text="", final=True) if transcription.eou else None
        best = transcription.results[0]
        text = (best.normalized_text or best.text).strip()
        if transcription.eou:
            logger.debug("EOU: {reason}", reason=pb.EouReason.Name(transcription.eou_reason))
        return Transcript(text=text, final=transcription.eou)
