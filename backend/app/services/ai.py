import hashlib
import json
import logging
import time
from collections import OrderedDict, deque

from fastapi import HTTPException, status

from app.core.config import settings
from app.services.llm import LLMProvider

logger = logging.getLogger(__name__)

RATE_LIMIT_CALLS = 5
RATE_LIMIT_WINDOW_SEC = 60
CACHE_TTL_SEC = 60 * 60 * 24

# ── in-memory fallback (REDIS_URL 미설정 또는 Redis 장애 시) ──
# 단일 프로세스 한정·재시작 시 초기화되므로 프로덕션은 Redis 사용 권장.
_CACHE_MAX = 512
_cache: OrderedDict[str, dict] = OrderedDict()
_calls: dict[int, deque] = {}

_redis = None


def _get_redis():
    """REDIS_URL이 있으면 lazy 싱글턴 client. 없으면 None (in-memory 경로)."""
    global _redis
    if not settings.REDIS_URL:
        return None
    if _redis is None:
        import redis.asyncio as aioredis

        _redis = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
    return _redis


def reset_state() -> None:
    """테스트용: in-memory 캐시·rate limit 초기화."""
    _cache.clear()
    _calls.clear()


async def redis_status() -> str:
    """/health용 연결 상태: ok(연결됨) / off(REDIS_URL 미설정 — in-memory) / error(연결 실패)."""
    r = _get_redis()
    if r is None:
        return "off"
    try:
        await r.ping()
        return "ok"
    except Exception:
        return "error"


def _cache_key(task: str, text: str) -> str:
    return hashlib.sha256(f"{task}:{text}".encode()).hexdigest()


def _rate_limit_exc() -> HTTPException:
    return HTTPException(
        status.HTTP_429_TOO_MANY_REQUESTS,
        f"AI 요청이 너무 잦아요. {RATE_LIMIT_WINDOW_SEC}초에 {RATE_LIMIT_CALLS}회까지 가능해요.",
    )


def _check_rate_limit_memory(user_id: int) -> None:
    now = time.monotonic()
    window = _calls.setdefault(user_id, deque())
    while window and now - window[0] > RATE_LIMIT_WINDOW_SEC:
        window.popleft()
    if len(window) >= RATE_LIMIT_CALLS:
        raise _rate_limit_exc()
    window.append(now)


async def check_rate_limit(user_id: int) -> None:
    """Redis 고정 윈도우(INCR+EXPIRE) — 재시작·멀티 워커에서도 유지.
    Redis 장애 시 fail-open으로 in-memory fallback (요청 자체는 막지 않음)."""
    r = _get_redis()
    if r is not None:
        key = f"ai:rl:{user_id}"
        try:
            count = await r.incr(key)
            # nx=True: TTL 없는 키에만 설정 — EXPIRE 유실로 인한 영구 차단 자가치유
            await r.expire(key, RATE_LIMIT_WINDOW_SEC, nx=True)
            if count > RATE_LIMIT_CALLS:
                raise _rate_limit_exc()
            return
        except HTTPException:
            raise
        except Exception:
            logger.warning("Redis rate limit unavailable — in-memory fallback", exc_info=True)
    _check_rate_limit_memory(user_id)


async def _cache_get(key: str) -> dict | None:
    r = _get_redis()
    if r is not None:
        try:
            raw = await r.get(f"ai:cache:{key}")
            return json.loads(raw) if raw else None
        except Exception:
            logger.warning("Redis cache get failed — in-memory fallback", exc_info=True)
    return _cache.get(key)


async def _cache_set(key: str, value: dict) -> None:
    r = _get_redis()
    if r is not None:
        try:
            await r.setex(
                f"ai:cache:{key}", CACHE_TTL_SEC, json.dumps(value, ensure_ascii=False)
            )
            return
        except Exception:
            logger.warning("Redis cache set failed — in-memory fallback", exc_info=True)
    _cache[key] = value
    if len(_cache) > _CACHE_MAX:
        _cache.popitem(last=False)


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
    cached = await _cache_get(key)
    if cached is not None:
        return {**cached, "cached": True}
    raw = await provider.generate(template.format(text=text))
    result = _parse_json(raw)
    await _cache_set(key, result)
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
