from collections.abc import AsyncIterator

import pytest

from voicebot.dialog.sentences import split_sentences


async def stream(*chunks: str) -> AsyncIterator[str]:
    for chunk in chunks:
        yield chunk


async def collect(chunks: AsyncIterator[str], min_length: int = 30) -> list[str]:
    return [sentence async for sentence in split_sentences(chunks, min_length)]


async def test_splits_stream_into_sentences():
    chunks = stream(
        "Москва — столица России. Население", " около тринадцати миллионов человек! Ещё", " вопросы?"
    )
    assert await collect(chunks, min_length=10) == [
        "Москва — столица России.",
        "Население около тринадцати миллионов человек!",
        "Ещё вопросы?",
    ]


async def test_merges_short_sentences():
    assert await collect(stream("Да. Конечно. Сейчас расскажу подробнее.")) == [
        "Да. Конечно. Сейчас расскажу подробнее.",
    ]


@pytest.mark.parametrize("chunks", [(), ("",), (" ", "  ")])
async def test_empty_stream(chunks):
    assert await collect(stream(*chunks)) == []


async def test_keeps_tail_without_punctuation():
    assert await collect(stream("Первое длинное предложение ответа. А это хвост"), min_length=5) == [
        "Первое длинное предложение ответа.",
        "А это хвост",
    ]
