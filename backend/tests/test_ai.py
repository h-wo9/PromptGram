import json

import pytest

from app.main import app
from app.services import ai as ai_service
from app.services.llm import LLMProvider, get_provider


class FakeProvider(LLMProvider):
    def __init__(self):
        self.calls = 0

    async def generate(self, prompt: str) -> str:
        self.calls += 1
        if "해시태그" in prompt:
            return json.dumps({"tags": ["#개발", "코드리뷰", "Python", "", "품질"]})
        return json.dumps(
            {"improved_prompt": "개선된 [주제] 프롬프트", "reasons": ["이유1", "이유2"]}
        )


@pytest.fixture
def fake_provider():
    provider = FakeProvider()
    ai_service.reset_state()
    app.dependency_overrides[get_provider] = lambda: provider
    yield provider
    app.dependency_overrides.pop(get_provider, None)
    ai_service.reset_state()


async def test_tune_structure_and_cache(auth_client, fake_provider):
    body = {"prompt_text": "코드 리뷰해줘"}
    res = await auth_client.post("/ai/tune", json=body)
    assert res.status_code == 200
    data = res.json()
    assert data["improved_prompt"] == "개선된 [주제] 프롬프트"
    assert data["reasons"] == ["이유1", "이유2"]
    assert data["cached"] is False
    assert fake_provider.calls == 1

    # 캐시 hit: provider 재호출 없음
    res = await auth_client.post("/ai/tune", json=body)
    assert res.json()["cached"] is True
    assert fake_provider.calls == 1

    # 다른 입력은 재호출
    res = await auth_client.post("/ai/tune", json={"prompt_text": "다른 프롬프트야"})
    assert res.json()["cached"] is False
    assert fake_provider.calls == 2


async def test_suggest_tags_normalized(auth_client, fake_provider):
    res = await auth_client.post("/ai/suggest-tags", json={"prompt_text": "파이썬 코드 리뷰"})
    assert res.status_code == 200
    tags = res.json()["tags"]
    assert 3 <= len(tags) <= 5
    assert "개발" in tags  # '#' 제거 확인
    assert "" not in tags


async def test_rate_limit_429(auth_client, fake_provider):
    for i in range(ai_service.RATE_LIMIT_CALLS):
        res = await auth_client.post("/ai/tune", json={"prompt_text": f"프롬프트 {i}번"})
        assert res.status_code == 200
    res = await auth_client.post("/ai/tune", json={"prompt_text": "한도 초과 요청"})
    assert res.status_code == 429


async def test_ai_requires_auth(client, fake_provider):
    res = await client.post("/ai/tune", json={"prompt_text": "인증 없는 요청"})
    assert res.status_code == 401
