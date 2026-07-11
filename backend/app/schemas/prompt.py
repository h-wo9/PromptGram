from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _normalize_tags(tags: list[str]) -> list[str]:
    seen: dict[str, None] = {}
    for tag in tags:
        name = tag.strip().lstrip("#").strip().lower()
        if name:
            seen.setdefault(name)
    return list(seen)


class PromptCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    prompt_text: str = Field(min_length=1, max_length=5000)
    ai_response: str | None = Field(default=None, max_length=20000)
    ai_source: str | None = Field(default=None, max_length=50)
    tags: list[str] = Field(default_factory=list, max_length=10)
    is_public: bool = True

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, v: list[str]) -> list[str]:
        tags = _normalize_tags(v)
        if any(len(t) > 50 for t in tags):
            raise ValueError("tag must be 50 characters or fewer")
        return tags


class PromptUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    prompt_text: str | None = Field(default=None, min_length=1, max_length=5000)
    ai_response: str | None = Field(default=None, max_length=20000)
    ai_source: str | None = Field(default=None, max_length=50)
    tags: list[str] | None = Field(default=None, max_length=10)
    is_public: bool | None = None

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        tags = _normalize_tags(v)
        if any(len(t) > 50 for t in tags):
            raise ValueError("tag must be 50 characters or fewer")
        return tags


class AuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nickname: str
    profile_image_url: str | None


class PromptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    prompt_text: str
    ai_response: str | None
    ai_source: str | None
    variables: list[str]
    is_public: bool
    like_count: int
    bookmark_count: int
    copy_count: int
    created_at: datetime
    updated_at: datetime
    author: AuthorOut
    tags: list[str]
    is_liked: bool = False
    is_bookmarked: bool = False


class FeedOut(BaseModel):
    items: list[PromptOut]
    next_cursor: str | None
