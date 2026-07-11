from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Prompt, PromptTag, Tag


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
