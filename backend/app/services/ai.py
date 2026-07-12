import hashlib
import json
import time
from collections import OrderedDict, deque

from fastapi import HTTPException, status

from app.services.llm import LLMProvider

# ── 응답 캐싱: 동일 입력 재호출 방지 (in-memory, FIFO 상한) ──
_CACHE_MAX = 512
_cache: OrderedDict[str, dict] = OrderedDict()

# ── per-user rate limit: sliding window ──
RATE_LIMIT_CALLS = 5
RATE_LIMIT_WINDOW_SEC = 60
_calls: dict[int, deque] = {}


def reset_state() -> None:
    """테스트용: 캐시·rate limit 초기화."""
    _cache.clear()
    _calls.clear()


def _cache_key(task: str, text: str) -> str:
    return hashlib.sha256(f"{task}:{text}".encode()).hexdigest()


def check_rate_limit(user_id: int) -> None:
    now = time.monotonic()
    window = _calls.setdefault(user_id, deque())
    while window and now - window[0] > RATE_LIMIT_WINDOW_SEC:
        window.popleft()
    if len(window) >= RATE_LIMIT_CALLS:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            f"AI 요청이 너무 잦아요. {RATE_LIMIT_WINDOW_SEC}초에 {RATE_LIMIT_CALLS}회까지 가능해요.",
        )
    window.append(now)


def _parse_json(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        text = text.removeprefix("json").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY, "LLM returned malformed JSON"
        )


TUNE_PROMPT = """당신은 프롬프트 엔지니어링 전문가다. 아래 사용자의 프롬프트 초안을 더 구체적이고 명확하게 개선하라.
[변수명] 형태의 변수 문법은 그대로 보존하거나 재사용성이 높아지도록 확장하라.
반드시 아래 JSON 형식으로만 답하라 (다른 텍스트 금지):
{{"improved_prompt": "<개선된 프롬프트>", "reasons": ["<개선 이유 1>", "<개선 이유 2>", "<개선 이유 3>"]}}

사용자 프롬프트 초안:
{text}"""

SUGGEST_TAGS_PROMPT = """아래 AI 프롬프트의 내용을 분석해 한국어 해시태그 3~5개를 추천하라.
태그는 짧은 명사형(예: 개발, 글쓰기, 마케팅, 영어학습)으로, # 없이.
반드시 아래 JSON 형식으로만 답하라 (다른 텍스트 금지):
{{"tags": ["태그1", "태그2", "태그3"]}}

프롬프트:
{text}"""


async def _cached_call(provider: LLMProvider, task: str, template: str, text: str) -> dict:
    key = _cache_key(task, text)
    if key in _cache:
        return {**_cache[key], "cached": True}
    raw = await provider.generate(template.format(text=text))
    result = _parse_json(raw)
    _cache[key] = result
    if len(_cache) > _CACHE_MAX:
        _cache.popitem(last=False)
    return {**result, "cached": False}


async def tune_prompt(provider: LLMProvider, text: str) -> dict:
    data = await _cached_call(provider, "tune", TUNE_PROMPT, text)
    if not isinstance(data.get("improved_prompt"), str) or not isinstance(
        data.get("reasons"), list
    ):
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "LLM returned malformed JSON")
    return data


async def suggest_tags(provider: LLMProvider, text: str) -> dict:
    data = await _cached_call(provider, "tags", SUGGEST_TAGS_PROMPT, text)
    tags = data.get("tags")
    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "LLM returned malformed JSON")
    data["tags"] = [t.strip().lstrip("#") for t in tags if t.strip()][:5]
    return data
