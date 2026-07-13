from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Bookmark, CopyRecord, Like, Prompt, PromptTag, Tag


PROMPT_LOAD_OPTIONS = (
    selectinload(Prompt.tags),
    selectinload(Prompt.author),
)


async def upsert_tags(db: AsyncSession, names: list[str]) -> list[Tag]:
    if not names:
        return []
    existing = (
        await db.scalars(select(Tag).where(Tag.name.in_(names)))
    ).all()
    by_name = {t.name: t for t in existing}
    for name in names:
        if name not in by_name:
            tag = Tag(name=name)
            db.add(tag)
            by_name[name] = tag
    await db.flush()
    return [by_name[name] for name in names]


async def set_prompt_tags(db: AsyncSession, prompt_id: int, tag_names: list[str]) -> None:
    tags = await upsert_tags(db, tag_names)
    existing = (
        await db.scalars(select(PromptTag).where(PromptTag.prompt_id == prompt_id))
    ).all()
    wanted_ids = {t.id for t in tags}
    for link in existing:
        if link.tag_id not in wanted_ids:
            await db.delete(link)
    existing_ids = {link.tag_id for link in existing}
    for tag in tags:
        if tag.id not in existing_ids:
            db.add(PromptTag(prompt_id=prompt_id, tag_id=tag.id))
    await db.flush()


async def get_prompt(db: AsyncSession, prompt_id: int) -> Prompt | None:
    return await db.scalar(
        select(Prompt)
        .where(Prompt.id == prompt_id)
        .options(*PROMPT_LOAD_OPTIONS)
        .execution_options(populate_existing=True)
    )


async def create_prompt(
    db: AsyncSession,
    *,
    user_id: int,
    title: str,
    prompt_text: str,
    ai_response: str | None,
    ai_source: str | None,
    variables: list[str],
    is_public: bool,
    tag_names: list[str],
) -> Prompt:
    prompt = Prompt(
        user_id=user_id,
        title=title,
        prompt_text=prompt_text,
        ai_response=ai_response,
        ai_source=ai_source,
        variables=variables,
        is_public=is_public,
    )
    db.add(prompt)
    await db.flush()
    await set_prompt_tags(db, prompt.id, tag_names)
    await db.commit()
    return await get_prompt(db, prompt.id)


def _apply_cursor(query, sort: str, cursor_key: tuple | None):
    if cursor_key is None:
        return query
    key, last_id = cursor_key
    if sort == "popular":
        return query.where(
            or_(
                Prompt.like_count < key,
                and_(Prompt.like_count == key, Prompt.id < last_id),
            )
        )
    return query.where(
        or_(
            Prompt.created_at < key,
            and_(Prompt.created_at == key, Prompt.id < last_id),
        )
    )


def _escape_like(q: str) -> str:
    """ILIKE 패턴 메타문자 이스케이프"""
    return q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


async def get_feed(
    db: AsyncSession,
    *,
    sort: str = "latest",
    tag: str | None = None,
    q: str | None = None,
    cursor_key: tuple[datetime | int, int] | None = None,
    limit: int = 12,
) -> list[Prompt]:
    query = (
        select(Prompt)
        .where(Prompt.is_public.is_(True))
        .options(*PROMPT_LOAD_OPTIONS)
        .limit(limit)
    )
    if tag:
        query = query.join(PromptTag, PromptTag.prompt_id == Prompt.id).join(
            Tag, and_(Tag.id == PromptTag.tag_id, Tag.name == tag)
        )
    if q:
        # pg_trgm GIN 인덱스(title/prompt_text)가 가속하는 부분 문자열 검색
        pattern = f"%{_escape_like(q)}%"
        query = query.where(
            or_(
                Prompt.title.ilike(pattern, escape="\\"),
                Prompt.prompt_text.ilike(pattern, escape="\\"),
            )
        )
    if sort == "popular":
        query = query.order_by(Prompt.like_count.desc(), Prompt.id.desc())
    else:
        query = query.order_by(Prompt.created_at.desc(), Prompt.id.desc())
    query = _apply_cursor(query, sort, cursor_key)
    return list((await db.scalars(query)).all())


async def toggle_like(db: AsyncSession, user_id: int, prompt: Prompt) -> bool:
    """토글 결과 liked 여부 반환. counter도 함께 갱신."""
    existing = await db.get(Like, (user_id, prompt.id))
    if existing:
        await db.delete(existing)
        prompt.like_count = max(0, prompt.like_count - 1)
        liked = False
    else:
        db.add(Like(user_id=user_id, prompt_id=prompt.id))
        prompt.like_count += 1
        liked = True
    await db.commit()
    return liked


async def toggle_bookmark(db: AsyncSession, user_id: int, prompt: Prompt) -> bool:
    existing = await db.get(Bookmark, (user_id, prompt.id))
    if existing:
        await db.delete(existing)
        prompt.bookmark_count = max(0, prompt.bookmark_count - 1)
        bookmarked = False
    else:
        db.add(Bookmark(user_id=user_id, prompt_id=prompt.id))
        prompt.bookmark_count += 1
        bookmarked = True
    await db.commit()
    return bookmarked


async def increase_copy_count(db: AsyncSession, prompt: Prompt, user_id: int | None) -> None:
    """복사는 무제한이지만 copy_count는 계정당 1회만. 비로그인 복사는 카운트 안 함."""
    if user_id is None:
        return
    if await db.get(CopyRecord, (user_id, prompt.id)):
        return
    db.add(CopyRecord(user_id=user_id, prompt_id=prompt.id))
    prompt.copy_count += 1
    await db.commit()


async def get_user_prompts(
    db: AsyncSession, user_id: int, *, public_only: bool = False
) -> list[Prompt]:
    query = (
        select(Prompt)
        .where(Prompt.user_id == user_id)
        .options(*PROMPT_LOAD_OPTIONS)
        .order_by(Prompt.created_at.desc(), Prompt.id.desc())
    )
    if public_only:
        query = query.where(Prompt.is_public.is_(True))
    return list((await db.scalars(query)).all())


async def get_user_bookmarks(db: AsyncSession, user_id: int) -> list[Prompt]:
    query = (
        select(Prompt)
        .join(Bookmark, Bookmark.prompt_id == Prompt.id)
        .where(Bookmark.user_id == user_id)
        .options(*PROMPT_LOAD_OPTIONS)
        .order_by(Bookmark.created_at.desc())
    )
    return list((await db.scalars(query)).all())


async def get_interaction_ids(
    db: AsyncSession, user_id: int | None, prompt_ids: list[int]
) -> tuple[set[int], set[int]]:
    """현재 사용자의 (liked_ids, bookmarked_ids)를 한 번의 왕복씩으로 조회 (N+1 방지)."""
    if user_id is None or not prompt_ids:
        return set(), set()
    liked = set(
        (
            await db.scalars(
                select(Like.prompt_id).where(
                    Like.user_id == user_id, Like.prompt_id.in_(prompt_ids)
                )
            )
        ).all()
    )
    bookmarked = set(
        (
            await db.scalars(
                select(Bookmark.prompt_id).where(
                    Bookmark.user_id == user_id, Bookmark.prompt_id.in_(prompt_ids)
                )
            )
        ).all()
    )
    return liked, bookmarked
