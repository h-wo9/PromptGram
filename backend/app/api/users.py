from fastapi import APIRouter

from app.api.deps import CurrentUser, DbDep
from app.api.prompts import to_prompt_out
from app.crud import prompt as prompt_crud
from app.schemas.prompt import PromptOut
from app.schemas.user import UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(user: CurrentUser):
    return user


@router.patch("/me", response_model=UserOut)
async def update_me(body: UserUpdate, user: CurrentUser, db: DbDep):
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/me/prompts", response_model=list[PromptOut])
async def my_prompts(user: CurrentUser, db: DbDep):
    prompts = await prompt_crud.get_user_prompts(db, user.id)
    liked, bookmarked = await prompt_crud.get_interaction_ids(
        db, user.id, [p.id for p in prompts]
    )
    return [to_prompt_out(p, liked, bookmarked) for p in prompts]


@router.get("/me/bookmarks", response_model=list[PromptOut])
async def my_bookmarks(user: CurrentUser, db: DbDep):
    prompts = await prompt_crud.get_user_bookmarks(db, user.id)
    liked, bookmarked = await prompt_crud.get_interaction_ids(
        db, user.id, [p.id for p in prompts]
    )
    return [to_prompt_out(p, liked, bookmarked) for p in prompts]
