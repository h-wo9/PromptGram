from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (Index("ix_comments_prompt_created", "prompt_id", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    prompt_id: Mapped[int] = mapped_column(
        ForeignKey("prompts.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    # 수정 시에만 설정 — FE에서 "(수정됨)" 표시 근거
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    author: Mapped["User"] = relationship(lazy="raise")


from app.models.user import User  # noqa: E402