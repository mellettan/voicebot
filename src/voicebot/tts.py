from typing import Protocol

import httpx

from voicebot.auth import TokenProvider


class SynthesisError(RuntimeError):
    """Ошибка синтеза речи."""


class Synthesizer(Protocol):
    async def synthesize(self, text: str) -> bytes: ...


class SaluteSpeechSynthesizer:
    """Синтез речи через REST API SaluteSpeech."""

    def __init__(
        self,
        http: httpx.AsyncClient,
        tokens: TokenProvider,
        rest_url: str,
        voice: str,
        audio_format: str,
    ) -> None:
        self._http = http
        self._tokens = tokens
        self._url = f"{rest_url.rstrip('/')}/text:synthesize"
        self._params = {"voice": voice, "format": audio_format}

    async def synthesize(self, text: str) -> bytes:
        """Возвращает аудио в формате WAV для переданного текста."""
        token = await self._tokens.get_token()
        try:
            response = await self._http.post(
                self._url,
                params=self._params,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/text"},
                content=text.encode(),
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise SynthesisError(f"Синтез не удался: {exc}") from exc
        return response.content
