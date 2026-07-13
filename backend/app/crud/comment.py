from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Comment


async def list_by_prompt(db: AsyncSession, prompt_id: int) -> list[Comment]:
    query = (
        select(Comment)
        .where(Comment.prompt_id == prompt_id)
        .options(selectinload(Comment.author))
        .order_by(Comment.created_at.desc(), Comment.id.desc())
    )
    return list((await db.scalars(query)).all())


async def get(db: AsyncSession, comment_id: int) -> Comment | None:
    return await db.scalar(
        select(Comment)
        .where(Comment.id == comment_id)
        .options(selectinload(Comment.author))
    )


async def create(db: AsyncSession, *, prompt_id: int, user_id: int, content: str) -> Comment:
    comment = Comment(prompt_id=prompt_id, user_id=user_id, content=content)
    db.add(comment)
    await db.commit()
    return await get(db, comment.id)


async def update(db: AsyncSession, comment: Comment, content: str) -> Comment:
    comment.content = content
    comment.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return comment


async def delete(db: AsyncSession, comment: Comment) -> None:
    await db.delete(comment)
    await db.commit()
