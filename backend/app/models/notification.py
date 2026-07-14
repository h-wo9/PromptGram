from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Notification(Base):
    """알림: follow(팔로우받음) / new_prompt(팔로잉이 글 게시) / comment(내 글에 댓글)"""

    __tablename__ = "notifications"
    __table_args__ = (Index("ix_notifications_user_created", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )  # 수신자
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(20))
    prompt_id: Mapped[int | None] = mapped_column(
        ForeignKey("prompts.id", ondelete="CASCADE")
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    actor: Mapped["User"] = relationship(foreign_keys=[actor_id], lazy="raise")
    prompt: Mapped["Prompt | None"] = relationship(lazy="raise")


from app.models.prompt import Prompt  # noqa: E402
from app.models.user import User  # noqa: E402