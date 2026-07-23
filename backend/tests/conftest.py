import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.db import Base, get_db
from app.main import app
from app.services import ai as ai_service


@pytest.fixture(autouse=True)
def _force_inmemory_ai(monkeypatch):
    """테스트는 항상 in-memory 경로 — 로컬 .env의 REDIS_URL이 있어도
    실제 Redis에 rate limit·캐시가 남아 테스트 간 오염되는 것을 방지."""
    monkeypatch.setattr(settings, "REDIS_URL", "")
    monkeypatch.setattr(ai_service, "_redis", None)


@pytest.fixture
async def client():
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.fixture
async def auth_client(client):
    await client.post(
        "/auth/signup",
        json={"email": "t@t.com", "password": "password123", "nickname": "tester"},
    )
    res = await client.post(
        "/auth/login", json={"email": "t@t.com", "password": "password123"}
    )
    client.headers["Authorization"] = f"Bearer {res.json()['access_token']}"
    return client
