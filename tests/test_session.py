import asyncio
import json
import time
from collections.abc import AsyncIterator

from fastapi.testclient import TestClient
from langchain_core.language_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from voicebot.app import Services, create_app
from voicebot.dialog.memory import DialogMemory
from voicebot.dialog.model import DialogModel
from voicebot.stt.recognizer import RecognitionError, Transcript


class FakeRecognizer:
    """Распознаёт фразу после двух аудиочанков, повторяя сценарий SaluteSpeech."""

    def __init__(self, phrases: list[str], fail_first: bool = False) -> None:
        self.phrases = phrases
        self.fail_first = fail_first
        self.received: list[bytes] = []

    async def recognize(self, audio: AsyncIterator[bytes]) -> AsyncIterator[Transcript]:
        if self.fail_first:
            self.fail_first = False
            raise RecognitionError("UNAVAILABLE: test")
        if not self.phrases:
            await asyncio.Event().wait()
        phrase = self.phrases.pop(0)
        self.received.append(await anext(audio))
        yield Transcript(text=phrase.split()[0], final=False)
        self.received.append(await anext(audio))
        yield Transcript(text=phrase, final=True)


class FakeSynthesizer:
    def __init__(self) -> None:
        self.texts: list[str] = []

    async def synthesize(self, text: str) -> bytes:
        self.texts.append(text)
        return f"RIFF:{text}".encode()


def build_client(redis, settings, recognizer, reply: str) -> tuple[TestClient, FakeSynthesizer]:
    synthesizer = FakeSynthesizer()
    chat = GenericFakeChatModel(messages=iter([AIMessage(reply)]))
    dialog = DialogModel(chat, DialogMemory(redis, 10, 600), system_prompt="test")
    services = Services(redis=redis, recognizer=recognizer, synthesizer=synthesizer, dialog=dialog)
    return TestClient(create_app(settings, services)), synthesizer


def receive_json(ws) -> dict:
    return json.loads(ws.receive_text())


def test_full_dialog_turn(redis, settings):
    reply = "Сейчас в Москве солнечно и тепло. Вечером возможен небольшой дождь."
    recognizer = FakeRecognizer(["какая погода в Москве"])
    client, synthesizer = build_client(redis, settings, recognizer, reply)

    with client, client.websocket_connect("/ws/voice?session=abc") as ws:
        assert receive_json(ws) == {"type": "session", "id": "abc"}
        ws.send_bytes(b"\x00\x01" * 800)
        assert receive_json(ws) == {"type": "transcription", "status": "partial", "text": "какая"}
        ws.send_bytes(b"\x02\x03" * 800)
        assert receive_json(ws) == {
            "type": "transcription",
            "status": "final",
            "text": "какая погода в Москве",
        }

        first = receive_json(ws)
        assert first == {"type": "response", "status": "partial", "text": "Сейчас в Москве солнечно и тепло."}
        audio = [ws.receive_bytes()]
        second = receive_json(ws)
        assert second["text"] == reply
        audio.append(ws.receive_bytes())
        assert receive_json(ws) == {"type": "response", "status": "final", "text": reply}
        ws.send_text(json.dumps({"type": "playback_finished"}))

    assert audio == [f"RIFF:{text}".encode() for text in synthesizer.texts]
    assert synthesizer.texts == ["Сейчас в Москве солнечно и тепло.", "Вечером возможен небольшой дождь."]
    assert recognizer.received == [b"\x00\x01" * 800, b"\x02\x03" * 800]


def test_recognition_error_is_reported_and_session_continues(redis, settings):
    recognizer = FakeRecognizer(["привет"], fail_first=True)
    client, _ = build_client(redis, settings, recognizer, "Здравствуйте!")

    with client, client.websocket_connect("/ws/voice") as ws:
        session = receive_json(ws)
        assert session["type"] == "session"
        assert len(session["id"]) == 32
        assert receive_json(ws)["type"] == "error"
        time.sleep(1.2)
        ws.send_bytes(b"\x00" * 3200)
        ws.send_bytes(b"\x00" * 3200)
        assert receive_json(ws)["status"] == "partial"
        assert receive_json(ws) == {"type": "transcription", "status": "final", "text": "привет"}


def test_healthcheck(redis, settings):
    client, _ = build_client(redis, settings, FakeRecognizer([]), "")
    with client:
        assert client.get("/healthz").json() == {"status": "ok"}
        assert "Голосовой ассистент" in client.get("/").text
