from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = (
        "postgresql+asyncpg://promptgram:promptgram@localhost:55432/promptgram"
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def normalize_db_scheme(cls, v: str) -> str:
        """Supabase/Render 등이 주는 postgres:// URL을 asyncpg 드라이버 스킴으로 변환.
        sslmode는 psycopg 전용 쿼리파라미터라 asyncpg.connect()가 모르는 kwarg로
        그대로 전달되면 TypeError가 나므로 asyncpg가 이해하는 ssl로 치환."""
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        parts = urlsplit(v)
        query = dict(parse_qsl(parts.query))
        if "sslmode" in query:
            query["ssl"] = query.pop("sslmode")
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
    JWT_SECRET_KEY: str = "dev-secret-do-not-use-in-prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14
    CORS_ORIGINS: str = "http://localhost:5173"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3-flash-preview"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
