from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser
from app.schemas.ai import AiTextIn, SuggestTagsOut, TuneOut
from app.services import ai as ai_service
from app.services.llm import LLMProvider, get_provider

router = APIRouter(prefix="/ai", tags=["ai"])

ProviderDep = Annotated[LLMProvider, Depends(get_provider)]


@router.post("/tune", response_model=TuneOut)
async def tune(body: AiTextIn, user: CurrentUser, provider: ProviderDep):
    """프롬프트 개선 '제안' (정답 아님) — 개선안 + 이유 반환."""
    await ai_service.check_rate_limit(user.id)
    return await ai_service.tune_prompt(provider, body.prompt_text)


@router.post("/suggest-tags", response_model=SuggestTagsOut)
async def suggest(body: AiTextIn, user: CurrentUser, provider: ProviderDep):
    await ai_service.check_rate_limit(user.id)
    return await ai_service.suggest_tags(provider, body.prompt_text)
