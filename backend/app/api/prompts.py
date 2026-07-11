from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbDep, OptionalUser
from app.crud import prompt as prompt_crud
from app.models import Prompt, User
from app.schemas.prompt import PromptCreate, PromptOut, PromptUpdate
from app.services.variables import parse_variables

router = APIRouter(prefix="/prompts", tags=["prompts"])


def to_prompt_out(
    prompt: Prompt,
    liked_ids: set[int] = frozenset(),
    bookmarked_ids: set[int] = frozenset(),
) -> PromptOut:
    return PromptOut(
        id=prompt.id,
        title=prompt.title,
        prompt_text=prompt.prompt_text,
        ai_response=prompt.ai_response,
        ai_source=prompt.ai_source,
        variables=prompt.variables or [],
        is_public=prompt.is_public,
        like_count=prompt.like_count,
        bookmark_count=prompt.bookmark_count,
        copy_count=prompt.copy_count,
        created_at=prompt.created_at,
        updated_at=prompt.updated_at,
        author=prompt.author,
        tags=[t.name for t in prompt.tags],
        is_liked=prompt.id in liked_ids,
        is_bookmarked=prompt.id in bookmarked_ids,
    )


def _get_owned(prompt: Prompt | None, user: User) -> Prompt:
    if prompt is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Prompt not found")
    if prompt.user_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not the author")
    return prompt


@router.post("", response_model=PromptOut, status_code=status.HTTP_201_CREATED)
async def create_prompt(body: PromptCreate, user: CurrentUser, db: DbDep):
    prompt = await prompt_crud.create_prompt(
        db,
        user_id=user.id,
        title=body.title,
        prompt_text=body.prompt_text,
        ai_response=body.ai_response,
        ai_source=body.ai_source,
        variables=parse_variables(body.prompt_text),
        is_public=body.is_public,
        tag_names=body.tags,
    )
    return to_prompt_out(prompt)


@router.get("/{prompt_id}", response_model=PromptOut)
async def get_prompt(prompt_id: int, db: DbDep, user: OptionalUser):
    prompt = await prompt_crud.get_prompt(db, prompt_id)
    if prompt is None or (
        not prompt.is_public and (user is None or prompt.user_id != user.id)
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Prompt not found")
    return to_prompt_out(prompt)


@router.patch("/{prompt_id}", response_model=PromptOut)
async def update_prompt(prompt_id: int, body: PromptUpdate, user: CurrentUser, db: DbDep):
    prompt = _get_owned(await prompt_crud.get_prompt(db, prompt_id), user)
    data = body.model_dump(exclude_unset=True)
    tags = data.pop("tags", None)
    for field, value in data.items():
        setattr(prompt, field, value)
    if "prompt_text" in data:
        prompt.variables = parse_variables(prompt.prompt_text)
    if tags is not None:
        await prompt_crud.set_prompt_tags(db, prompt.id, tags)
    await db.commit()
    return to_prompt_out(await prompt_crud.get_prompt(db, prompt_id))


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(prompt_id: int, user: CurrentUser, db: DbDep):
    prompt = _get_owned(await prompt_crud.get_prompt(db, prompt_id), user)
    await db.delete(prompt)
    await db.commit()
