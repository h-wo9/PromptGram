from pydantic import BaseModel, Field


class AiTextIn(BaseModel):
    prompt_text: str = Field(min_length=5, max_length=5000)


class TuneOut(BaseModel):
    improved_prompt: str
    reasons: list[str]
    cached: bool


class SuggestTagsOut(BaseModel):
    tags: list[str]
    cached: bool
