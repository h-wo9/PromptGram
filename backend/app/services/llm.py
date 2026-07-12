import asyncio
import random
from abc import ABC, abstractmethod

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class LLMProvider(ABC):
    """LLM 호출 인터페이스. 향후 OpenAI 등은 이 base를 구현한 클래스만 추가하면 됨."""

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """prompt를 보내고 텍스트 응답을 반환."""


class GeminiProvider(LLMProvider):
    """Gemini 3 Flash (무료 티어).

    주의(명세서 2-4): 무료 티어 입력·출력은 학습에 쓰일 수 있으므로 민감정보 금지.
    429는 exponential backoff + jitter로 재시도.
    """

    API_URL = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "{model}:generateContent"
    )
    MAX_RETRIES = 3

    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        self._api_key = api_key
        self._model = model

    async def generate(self, prompt: str) -> str:
        url = self.API_URL.format(model=self._model)
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        async with httpx.AsyncClient(timeout=60) as client:
            for attempt in range(self.MAX_RETRIES + 1):
                try:
                    res = await client.post(
                        url, json=body, headers={"x-goog-api-key": self._api_key}
                    )
                except httpx.TimeoutException:
                    raise HTTPException(
                        status.HTTP_504_GATEWAY_TIMEOUT, "LLM request timed out"
                    )
                if res.status_code == 429 and attempt < self.MAX_RETRIES:
                    await asyncio.sleep(2**attempt + random.random())
                    continue
                if res.status_code != 200:
                    raise HTTPException(
                        status.HTTP_502_BAD_GATEWAY,
                        f"LLM upstream error ({res.status_code})",
                    )
                data = res.json()
                try:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError):
                    raise HTTPException(
                        status.HTTP_502_BAD_GATEWAY, "LLM returned unexpected response"
                    )
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "LLM rate limited")


_provider: LLMProvider | None = None


def get_provider() -> LLMProvider:
    global _provider
    if _provider is None:
        _provider = GeminiProvider(settings.GEMINI_API_KEY, settings.GEMINI_MODEL)
    return _provider
