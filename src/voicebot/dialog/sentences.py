import re
from collections.abc import AsyncIterator

_SENTENCE_END = re.compile(r"(?<=[.!?…])\s+")


async def split_sentences(chunks: AsyncIterator[str], min_length: int = 30) -> AsyncIterator[str]:
    """Собирает поток токенов LLM в предложения для синтеза речи.

    Короткие предложения склеиваются до `min_length` символов: так синтез не дробится
    на мелкие запросы, а первая фраза уходит в TTS, не дожидаясь конца ответа.
    """
    buffer = ""
    pending = ""
    async for chunk in chunks:
        buffer += chunk
        *complete, buffer = _SENTENCE_END.split(buffer)
        for sentence in complete:
            pending = f"{pending} {sentence}".strip()
            if len(pending) >= min_length:
                yield pending
                pending = ""
    tail = f"{pending} {buffer}".strip()
    if tail:
        yield tail
