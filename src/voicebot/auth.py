import asyncio
import time
import uuid

import httpx
from loguru import logger
from redis.asyncio import Redis


class SberAuthError(RuntimeError):
    """Не удалось получить access token в Sber OAuth."""


class TokenProvider:
    """Выдаёт access token Sber OAuth и кэширует его в Redis до истечения срока действия.

    Токен живёт 30 минут и общий для всех воркеров, поэтому хранится в Redis, а не в памяти
    процесса. Обновление выполняется заранее, за `refresh_margin` секунд до истечения.
    """

    def __init__(
        self,
        redis: Redis,
        http: httpx.AsyncClient,
        oauth_url: str,
        auth_key: str,
        scope: str,
        refresh_margin: float = 60.0,
    ) -> None:
        self._redis = redis
        self._http = http
        self._oauth_url = oauth_url
        self._auth_key = auth_key
        self._scope = scope
        self._refresh_margin_ms = int(refresh_margin * 1000)
        self._cache_key = f"voicebot:token:{scope}"
        self._lock = asyncio.Lock()

    async def get_token(self) -> str:
        """Возвращает действующий токен из кэша или запрашивает новый."""
        if token := await self._redis.get(self._cache_key):
            return token
        async with self._lock:
            if token := await self._redis.get(self._cache_key):
                return token
            token, expires_at_ms = await self._request_token()
            ttl_ms = expires_at_ms - int(time.time() * 1000) - self._refresh_margin_ms
            if ttl_ms > 0:
                await self._redis.set(self._cache_key, token, px=ttl_ms)
            logger.info("Получен новый токен {scope}, ttl={ttl}s", scope=self._scope, ttl=ttl_ms // 1000)
            return token

    async def _request_token(self) -> tuple[str, int]:
        try:
            response = await self._http.post(
                self._oauth_url,
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Basic {self._auth_key}",
                    "RqUID": str(uuid.uuid4()),
                },
                data={"scope": self._scope},
            )
            response.raise_for_status()
            payload = response.json()
            return payload["access_token"], int(payload["expires_at"])
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise SberAuthError(f"Не удалось получить токен для {self._scope}: {exc}") from exc
