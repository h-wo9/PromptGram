from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    return await db.scalar(select(User).where(User.email == email))


async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def create(db: AsyncSession, *, email: str, password_hash: str, nickname: str) -> User:
    user = User(email=email, password_hash=password_hash, nickname=nickname)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
