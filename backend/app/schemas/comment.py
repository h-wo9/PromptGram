from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.prompt import AuthorOut


class CommentIn(BaseModel):
    content: str = Field(min_length=1, max_length=500)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    created_at: datetime
    updated_at: datetime | None
    author: AuthorOut
