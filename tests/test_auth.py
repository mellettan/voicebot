import asyncio
import time

import httpx
import pytest

from voicebot.auth import SberAuthError, TokenProvider


def make_provider(redis, handler) -> TokenProvider:
    http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return TokenProvider(redis, http, "https://oauth.test/api/v2/oauth", "secret", "SALUTE_SPEECH_PERS")


def token_response(token: str, ttl_seconds: int = 1800) -> httpx.Response:
    expires_at = int((time.time() + ttl_seconds) * 1000)
    return httpx.Response(200, json={"access_token": token, "expires_at": expires_at})


async def test_requests_token_once_and_caches_it(redis):
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return token_response("token-1")

    provider = make_provider(redis, handler)

    assert await provider.get_token() == "token-1"
    assert await provider.get_token() == "token-1"
    assert len(calls) == 1
    assert calls[0].headers["Authorization"] == "Basic secret"
    assert calls[0].content == b"scope=SALUTE_SPEECH_PERS"
    assert 1700 < await redis.ttl("voicebot:token:SALUTE_SPEECH_PERS") <= 1740


async def test_concurrent_callers_share_single_request(redis):
    calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.01)
        return token_response("shared")

    provider = make_provider(redis, handler)
    tokens = await asyncio.gather(*(provider.get_token() for _ in range(10)))

    assert set(tokens) == {"shared"}
    assert calls == 1


async def test_does_not_cache_token_that_is_about_to_expire(redis):
    provider = make_provider(redis, lambda request: token_response("short", ttl_seconds=30))

    assert await provider.get_token() == "short"
    assert await redis.exists("voicebot:token:SALUTE_SPEECH_PERS") == 0


@pytest.mark.parametrize(
    "response",
    [httpx.Response(401, json={"message": "Unauthorized"}), httpx.Response(200, json={"unexpected": True})],
)
async def test_raises_on_bad_response(redis, response):
    provider = make_provider(redis, lambda request: response)

    with pytest.raises(SberAuthError):
        await provider.get_token()
