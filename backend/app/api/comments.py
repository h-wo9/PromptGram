from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbDep, OptionalUser
from app.api.prompts import _get_visible
from app.crud import comment as comment_crud
from app.models import Comment, User
from app.schemas.comment import CommentIn, CommentOut

router = APIRouter(tags=["comments"])


@router.get("/prompts/{prompt_id}/comments", response_model=list[CommentOut])
async def list_comments(prompt_id: int, db: DbDep, user: OptionalUser):
    await _get_visible(db, prompt_id, user)
    return await comment_crud.list_by_prompt(db, prompt_id)


@router.post(
    "/prompts/{prompt_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(prompt_id: int, body: CommentIn, user: CurrentUser, db: DbDep):
    await _get_visible(db, prompt_id, user)
    return await comment_crud.create(
        db, prompt_id=prompt_id, user_id=user.id, content=body.content
    )


async def _get_owned(db, comment_id: int, user: User) -> Comment:
    comment = await comment_crud.get(db, comment_id)
    if comment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Comment not found")
    if comment.user_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not the author")
    return comment


@router.patch("/comments/{comment_id}", response_model=CommentOut)
async def update_comment(comment_id: int, body: CommentIn, user: CurrentUser, db: DbDep):
    comment = await _get_owned(db, comment_id, user)
    return await comment_crud.update(db, comment, body.content)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: int, user: CurrentUser, db: DbDep):
    comment = await _get_owned(db, comment_id, user)
    await comment_crud.delete(db, comment)
