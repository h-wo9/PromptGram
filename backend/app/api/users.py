from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbDep, OptionalUser
from app.api.prompts import to_prompt_out
from app.crud import follow as follow_crud
from app.crud import prompt as prompt_crud
from app.crud import user as user_crud
from app.schemas.prompt import AuthorOut, PromptOut
from app.schemas.user import FollowToggleOut, UserOut, UserProfileOut, UserUpdate

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


# ── 공개 프로필 (path param 라우트는 /me* 뒤에 선언) ──


async def _get_user_or_404(db, user_id: int):
    target = await user_crud.get_by_id(db, user_id)
    if target is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return target


@router.get("/{user_id}", response_model=UserProfileOut)
async def get_profile(user_id: int, db: DbDep, user: OptionalUser):
    target = await _get_user_or_404(db, user_id)
    followers, following = await follow_crud.counts(db, user_id)
    return UserProfileOut(
        id=target.id,
        nickname=target.nickname,
        bio=target.bio,
        profile_image_url=target.profile_image_url,
        created_at=target.created_at,
        follower_count=followers,
        following_count=following,
        is_following=(
            await follow_crud.is_following(db, user.id, user_id) if user else False
        ),
    )


@router.get("/{user_id}/prompts", response_model=list[PromptOut])
async def user_public_prompts(user_id: int, db: DbDep, user: OptionalUser):
    await _get_user_or_404(db, user_id)
    prompts = await prompt_crud.get_user_prompts(db, user_id, public_only=True)
    liked, bookmarked = await prompt_crud.get_interaction_ids(
        db, user.id if user else None, [p.id for p in prompts]
    )
    return [to_prompt_out(p, liked, bookmarked) for p in prompts]


@router.post("/{user_id}/follow", response_model=FollowToggleOut)
async def follow_user(user_id: int, user: CurrentUser, db: DbDep):
    if user_id == user.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot follow yourself")
    await _get_user_or_404(db, user_id)
    is_following = await follow_crud.toggle(db, user.id, user_id)
    followers, _ = await follow_crud.counts(db, user_id)
    return FollowToggleOut(is_following=is_following, follower_count=followers)


@router.get("/{user_id}/followers", response_model=list[AuthorOut])
async def user_followers(user_id: int, db: DbDep):
    await _get_user_or_404(db, user_id)
    return await follow_crud.followers_of(db, user_id)


@router.get("/{user_id}/following", response_model=list[AuthorOut])
async def user_following(user_id: int, db: DbDep):
    await _get_user_or_404(db, user_id)
    return await follow_crud.following_of(db, user_id)
