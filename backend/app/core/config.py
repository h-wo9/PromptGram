from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = (
        "postgresql+asyncpg://promptgram:promptgram@localhost:55432/promptgram"
    )
    JWT_SECRET_KEY: str = "dev-secret-do-not-use-in-prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14
    CORS_ORIGINS: str = "http://localhost:5173"
    LLM_PROVIDER: str = "ollama"
    GEMINI_API_KEY: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
