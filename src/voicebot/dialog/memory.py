import json

from langchain_core.messages import BaseMessage, messages_from_dict, messages_to_dict
from redis.asyncio import Redis


class DialogMemory:
    """История диалога в Redis: последние `max_messages` реплик сессии с TTL.

    Хранение в Redis позволяет продолжить разговор после переподключения WebSocket
    и не зависеть от того, на какой воркер попал клиент.
    """

    def __init__(self, redis: Redis, max_messages: int, ttl_seconds: int) -> None:
        self._redis = redis
        self._max_messages = max_messages
        self._ttl_seconds = ttl_seconds

    @staticmethod
    def _key(session_id: str) -> str:
        return f"voicebot:dialog:{session_id}"

    async def load(self, session_id: str) -> list[BaseMessage]:
        """Возвращает историю сессии в хронологическом порядке."""
        raw = await self._redis.lrange(self._key(session_id), 0, -1)
        return messages_from_dict([json.loads(item) for item in raw])

    async def append(self, session_id: str, *messages: BaseMessage) -> None:
        """Дописывает реплики, обрезает историю и продлевает TTL одной транзакцией."""
        if not messages:
            return
        key = self._key(session_id)
        payload = [json.dumps(item, ensure_ascii=False) for item in messages_to_dict(list(messages))]
        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.rpush(key, *payload)
            pipe.ltrim(key, -self._max_messages, -1)
            pipe.expire(key, self._ttl_seconds)
            await pipe.execute()

    async def clear(self, session_id: str) -> None:
        """Удаляет историю сессии."""
        await self._redis.delete(self._key(session_id))
