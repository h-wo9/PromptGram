from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Follow, User


async def counts(db: AsyncSession, user_id: int) -> tuple[int, int]:
    """(follower_count, following_count)"""
    followers = await db.scalar(
        select(func.count()).select_from(Follow).where(Follow.following_id == user_id)
    )
    following = await db.scalar(
        select(func.count()).select_from(Follow).where(Follow.follower_id == user_id)
    )
    return followers or 0, following or 0


async def is_following(db: AsyncSession, follower_id: int, following_id: int) -> bool:
    return await db.get(Follow, (follower_id, following_id)) is not None


async def toggle(db: AsyncSession, follower_id: int, following_id: int) -> bool:
    """토글 후 팔로우 여부 반환. delete-first + savepoint로 동시 요청에도 안전."""
    deleted = await db.execute(
        delete(Follow).where(
            Follow.follower_id == follower_id, Follow.following_id == following_id
        )
    )
    if deleted.rowcount:
        result = False
    else:
        try:
            async with db.begin_nested():
                db.add(Follow(follower_id=follower_id, following_id=following_id))
                await db.flush()
        except IntegrityError:
            # 동시 요청이 먼저 팔로우 — 팔로잉 상태로 간주
            pass
        result = True
    await db.commit()
    return result


async def followers_of(db: AsyncSession, user_id: int) -> list[User]:
    query = (
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
        .order_by(Follow.created_at.desc())
    )
    return list((await db.scalars(query)).all())


async def following_of(db: AsyncSession, user_id: int) -> list[User]:
    query = (
        select(User)
        .join(Follow, Follow.following_id == User.id)
        .where(Follow.follower_id == user_id)
        .order_by(Follow.created_at.desc())
    )
    return list((await db.scalars(query)).all())
