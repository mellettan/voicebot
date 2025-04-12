from collections.abc import AsyncIterator

import grpc
import pytest

from voicebot.stt.proto import recognition_pb2 as pb
from voicebot.stt.proto.recognition_pb2_grpc import SmartSpeechServicer, add_SmartSpeechServicer_to_server
from voicebot.stt.recognizer import RecognitionConfig, RecognitionError, SaluteSpeechRecognizer, Transcript


class StaticTokens:
    async def get_token(self) -> str:
        return "token"


class FakeSmartSpeech(SmartSpeechServicer):
    """Отвечает частичной гипотезой на первый чанк и финальной с EOU на второй."""

    def __init__(self) -> None:
        self.options: pb.RecognitionOptions | None = None
        self.chunks: list[bytes] = []

    async def Recognize(self, request_iterator, context):
        async for request in request_iterator:
            if request.HasField("options"):
                self.options = request.options
                yield pb.RecognitionResponse(backend_info=pb.BackendInfo(model_name="general"))
                continue
            self.chunks.append(request.audio_chunk)
            if request.audio_chunk == b"boom":
                await context.abort(grpc.StatusCode.UNAVAILABLE, "backend is down")
            final = len(self.chunks) == 2
            text = "привет мир" if final else "привет"
            yield pb.RecognitionResponse(
                transcription=pb.Transcription(
                    results=[pb.Hypothesis(text=text, normalized_text=text.capitalize())],
                    eou=final,
                    eou_reason=pb.ORGANIC if final else pb.UNSPECIFIED,
                )
            )


@pytest.fixture
async def speech_server():
    servicer = FakeSmartSpeech()
    server = grpc.aio.server()
    add_SmartSpeechServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    await server.start()
    yield servicer, f"127.0.0.1:{port}"
    await server.stop(grace=None)


def make_recognizer(host: str) -> SaluteSpeechRecognizer:
    config = RecognitionConfig(
        host=host,
        sample_rate=16000,
        language="ru-RU",
        no_speech_timeout_seconds=7,
        max_speech_timeout_seconds=20,
        hints=["GigaChat"],
        use_tls=False,
    )
    return SaluteSpeechRecognizer(config, StaticTokens())


async def audio(*chunks: bytes) -> AsyncIterator[bytes]:
    for chunk in chunks:
        yield chunk


async def test_streams_partial_and_final_transcripts(speech_server):
    servicer, host = speech_server

    transcripts = [t async for t in make_recognizer(host).recognize(audio(b"one", b"two", b"three"))]

    assert transcripts == [Transcript("Привет", final=False), Transcript("Привет мир", final=True)]
    assert servicer.chunks == [b"one", b"two"]
    assert servicer.options.sample_rate == 16000
    assert servicer.options.audio_encoding == pb.RecognitionOptions.PCM_S16LE
    assert servicer.options.enable_partial_results.enable is True
    assert servicer.options.no_speech_timeout.seconds == 7
    assert list(servicer.options.hints.words) == ["GigaChat"]


async def test_wraps_grpc_errors(speech_server):
    _, host = speech_server

    with pytest.raises(RecognitionError, match="UNAVAILABLE"):
        async for _ in make_recognizer(host).recognize(audio(b"boom")):
            pass
