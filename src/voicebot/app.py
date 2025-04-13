import ssl
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

import httpx
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from langchain_gigachat.chat_models import GigaChat
from redis.asyncio import Redis

from voicebot.auth import TokenProvider
from voicebot.config import PACKAGE_DIR, Settings, get_settings
from voicebot.dialog.memory import DialogMemory
from voicebot.dialog.model import DialogModel
from voicebot.logs import setup_logging
from voicebot.session import VoiceSession
from voicebot.stt.recognizer import RecognitionConfig, Recognizer, SaluteSpeechRecognizer
from voicebot.tts import SaluteSpeechSynthesizer, Synthesizer


@dataclass(frozen=True, slots=True)
class Services:
    redis: Redis
    recognizer: Recognizer
    synthesizer: Synthesizer
    dialog: DialogModel


@asynccontextmanager
async def build_services(settings: Settings) -> AsyncIterator[Services]:
    """Создаёт клиенты внешних сервисов и закрывает их при остановке приложения."""
    ca_bundle = str(settings.sber_ca_bundle)
    ssl_context = ssl.create_default_context()
    ssl_context.load_verify_locations(cafile=ca_bundle)

    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    http = httpx.AsyncClient(verify=ssl_context, timeout=settings.http_timeout_seconds)
    try:
        speech_tokens = TokenProvider(
            redis=redis,
            http=http,
            oauth_url=settings.sber_oauth_url,
            auth_key=settings.salute_speech_auth_key.get_secret_value(),
            scope=settings.salute_speech_scope,
        )
        recognizer = SaluteSpeechRecognizer(
            config=RecognitionConfig(
                host=settings.salute_speech_grpc_host,
                sample_rate=settings.stt_sample_rate,
                language=settings.stt_language,
                no_speech_timeout_seconds=settings.stt_no_speech_timeout_seconds,
                max_speech_timeout_seconds=settings.stt_max_speech_timeout_seconds,
                hints=settings.stt_hints,
            ),
            tokens=speech_tokens,
            root_certificates=settings.sber_ca_bundle.read_bytes(),
        )
        synthesizer = SaluteSpeechSynthesizer(
            http=http,
            tokens=speech_tokens,
            rest_url=settings.salute_speech_rest_url,
            voice=settings.tts_voice,
            audio_format=settings.tts_format,
        )
        chat = GigaChat(
            credentials=settings.gigachat_auth_key.get_secret_value(),
            scope=settings.gigachat_scope,
            model=settings.gigachat_model,
            temperature=settings.gigachat_temperature,
            ca_bundle_file=ca_bundle,
            streaming=True,
        )
        dialog = DialogModel(
            chat=chat,
            memory=DialogMemory(redis, settings.dialog_max_messages, settings.dialog_ttl_seconds),
            system_prompt=settings.system_prompt,
        )
        yield Services(redis=redis, recognizer=recognizer, synthesizer=synthesizer, dialog=dialog)
    finally:
        await http.aclose()
        await redis.aclose()


def create_app(settings: Settings | None = None, services: Services | None = None) -> FastAPI:
    """Собирает FastAPI-приложение. `services` подменяются в тестах."""
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        setup_logging(settings.log_level, settings.log_json)
        if services is not None:
            app.state.services = services
            yield
            return
        async with build_services(settings) as built:
            app.state.services = built
            yield

    app = FastAPI(title="Voice assistant", lifespan=lifespan)

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        await app.state.services.redis.ping()
        return {"status": "ok"}

    @app.websocket("/ws/voice")
    async def voice(websocket: WebSocket, session: str | None = None) -> None:
        current: Services = websocket.app.state.services
        await websocket.accept()
        await VoiceSession(
            websocket=websocket,
            recognizer=current.recognizer,
            dialog=current.dialog,
            synthesizer=current.synthesizer,
            session_id=session,
            playback_timeout=settings.playback_timeout_seconds,
        ).run()

    app.mount("/", StaticFiles(directory=PACKAGE_DIR / "static", html=True), name="static")
    return app
