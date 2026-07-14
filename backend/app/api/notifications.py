from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbDep
from app.crud import notification as notification_crud
from app.schemas.notification import NotificationOut

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
async def my_notifications(user: CurrentUser, db: DbDep):
    notifications = await notification_crud.list_for(db, user.id)
    return [
        NotificationOut(
            id=n.id,
            type=n.type,
            is_read=n.is_read,
            created_at=n.created_at,
            actor=n.actor,
            prompt_id=n.prompt_id,
            prompt_title=n.prompt.title if n.prompt else None,
        )
        for n in notifications
    ]


@router.patch("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def read_notification(notification_id: int, user: CurrentUser, db: DbDep):
    if not await notification_crud.mark_read(db, user.id, notification_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def read_all_notifications(user: CurrentUser, db: DbDep):
    await notification_crud.mark_all_read(db, user.id)
