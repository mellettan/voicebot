import pytest
from fakeredis import FakeAsyncRedis

from voicebot.config import Settings


@pytest.fixture
async def redis():
    client = FakeAsyncRedis(decode_responses=True)
    yield client
    await client.flushall()
    await client.aclose()


@pytest.fixture
def settings() -> Settings:
    return Settings(_env_file=None, salute_speech_auth_key="speech-key", gigachat_auth_key="chat-key")
