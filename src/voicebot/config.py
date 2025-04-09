from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PACKAGE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Настройки сервиса из переменных окружения и файла `.env`."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    log_level: str = "INFO"
    log_json: bool = False
    redis_url: str = "redis://localhost:6379/0"

    sber_oauth_url: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    sber_ca_bundle: Path = PACKAGE_DIR / "certs" / "russian_trusted_root_ca.pem"
    http_timeout_seconds: float = 15.0

    salute_speech_auth_key: SecretStr
    salute_speech_scope: str = "SALUTE_SPEECH_PERS"
    salute_speech_grpc_host: str = "smartspeech.sber.ru"
    salute_speech_rest_url: str = "https://smartspeech.sber.ru/rest/v1"

    stt_sample_rate: int = 16000
    stt_language: str = "ru-RU"
    stt_no_speech_timeout_seconds: int = 7
    stt_max_speech_timeout_seconds: int = 20
    stt_hints: list[str] = []

    tts_voice: str = "Bys_24000"
    tts_format: str = "wav16"

    gigachat_auth_key: SecretStr
    gigachat_scope: str = "GIGACHAT_API_PERS"
    gigachat_model: str = "GigaChat"
    gigachat_temperature: float = 0.3
    system_prompt: str = (
        "Ты дружелюбный голосовой ассистент. Твой ответ будет озвучен, поэтому отвечай "
        "коротко, простыми предложениями, без списков, разметки и эмодзи."
    )

    dialog_max_messages: int = 20
    dialog_ttl_seconds: int = 3600
    playback_timeout_seconds: float = 60.0


@lru_cache
def get_settings() -> Settings:
    """Возвращает настройки, прочитанные один раз за время жизни процесса."""
    return Settings()
