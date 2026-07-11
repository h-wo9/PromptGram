from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import decode_token
from app.crud import user as user_crud
from app.models import User

_bearer = HTTPBearer(auto_error=False)

DbDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DbDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    user_id = decode_token(credentials.credentials, "access")
    if user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    user = await user_crud.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_user_optional(
    db: DbDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User | None:
    if credentials is None:
        return None
    user_id = decode_token(credentials.credentials, "access")
    if user_id is None:
        return None
    return await user_crud.get_by_id(db, user_id)


OptionalUser = Annotated[User | None, Depends(get_current_user_optional)]
