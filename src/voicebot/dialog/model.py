from collections.abc import AsyncIterator

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from voicebot.dialog.memory import DialogMemory


class DialogModel:
    """Генерирует ответ LLM с учётом истории диалога и сохраняет обмен репликами."""

    def __init__(self, chat: BaseChatModel, memory: DialogMemory, system_prompt: str) -> None:
        self._chat = chat
        self._memory = memory
        self._system_prompt = system_prompt

    async def stream_reply(self, session_id: str, text: str) -> AsyncIterator[str]:
        """Стримит ответ по токенам; в историю попадает только полностью полученный ответ."""
        history = await self._memory.load(session_id)
        messages = [SystemMessage(self._system_prompt), *history, HumanMessage(text)]
        parts: list[str] = []
        async for chunk in self._chat.astream(messages):
            if isinstance(chunk.content, str) and chunk.content:
                parts.append(chunk.content)
                yield chunk.content
        reply = "".join(parts).strip()
        if reply:
            await self._memory.append(session_id, HumanMessage(text), AIMessage(reply))
