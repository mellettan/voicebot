from langchain_core.language_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage

from voicebot.dialog.memory import DialogMemory
from voicebot.dialog.model import DialogModel


async def test_memory_trims_history_and_sets_ttl(redis):
    memory = DialogMemory(redis, max_messages=4, ttl_seconds=600)

    for index in range(3):
        await memory.append("s1", HumanMessage(f"вопрос {index}"), AIMessage(f"ответ {index}"))

    history = await memory.load("s1")
    assert [message.content for message in history] == ["вопрос 1", "ответ 1", "вопрос 2", "ответ 2"]
    assert isinstance(history[0], HumanMessage)
    assert isinstance(history[1], AIMessage)
    assert 0 < await redis.ttl("voicebot:dialog:s1") <= 600


async def test_sessions_are_isolated(redis):
    memory = DialogMemory(redis, max_messages=10, ttl_seconds=600)
    await memory.append("a", HumanMessage("привет"))

    assert await memory.load("b") == []
    await memory.clear("a")
    assert await memory.load("a") == []


async def test_reply_is_streamed_and_saved_to_history(redis):
    memory = DialogMemory(redis, max_messages=10, ttl_seconds=600)
    await memory.append("s1", HumanMessage("Меня зовут Роман"), AIMessage("Приятно познакомиться!"))
    chat = GenericFakeChatModel(messages=iter([AIMessage("Вас зовут Роман.")]))
    model = DialogModel(chat, memory, system_prompt="Ты голосовой ассистент")

    chunks = [chunk async for chunk in model.stream_reply("s1", "Как меня зовут?")]

    assert len(chunks) > 1
    assert "".join(chunks) == "Вас зовут Роман."
    history = await memory.load("s1")
    assert [message.content for message in history[-2:]] == ["Как меня зовут?", "Вас зовут Роман."]
