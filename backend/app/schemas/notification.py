from datetime import datetime

from pydantic import BaseModel

from app.schemas.prompt import AuthorOut


class NotificationOut(BaseModel):
    id: int
    type: str  # follow | new_prompt | comment
    is_read: bool
    created_at: datetime
    actor: AuthorOut
    prompt_id: int | None
    prompt_title: str | None
