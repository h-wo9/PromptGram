from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Notification

LIST_LIMIT = 30


def add(
    db: AsyncSession,
    *,
    user_id: int,
    actor_id: int,
    type: str,
    prompt_id: int | None = None,
) -> None:
    """세션에 알림 추가 (commit은 호출자 트랜잭션에 합류)"""
    db.add(
        Notification(user_id=user_id, actor_id=actor_id, type=type, prompt_id=prompt_id)
    )


async def list_for(db: AsyncSession, user_id: int) -> list[Notification]:
    query = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .options(selectinload(Notification.actor), selectinload(Notification.prompt))
        .order_by(Notification.created_at.desc(), Notification.id.desc())
        .limit(LIST_LIMIT)
    )
    return list((await db.scalars(query)).all())


async def mark_read(db: AsyncSession, user_id: int, notification_id: int) -> bool:
    notification = await db.get(Notification, notification_id)
    if notification is None or notification.user_id != user_id:
        return False
    notification.is_read = True
    await db.commit()
    return True


async def mark_all_read(db: AsyncSession, user_id: int) -> None:
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
    await db.commit()
