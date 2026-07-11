from fastapi import APIRouter, HTTPException, Request, Response, status

from app.api.deps import DbDep
from app.core.config import settings
from app.core.security import (
    REFRESH_COOKIE_NAME,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.crud import user as user_crud
from app.schemas.user import LoginIn, SignupIn, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_refresh_cookie(response: Response, user_id: int) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=create_refresh_token(user_id),
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/auth",
    )


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(body: SignupIn, db: DbDep):
    if await user_crud.get_by_email(db, body.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    return await user_crud.create(
        db,
        email=body.email,
        password_hash=hash_password(body.password),
        nickname=body.nickname,
    )


@router.post("/login", response_model=TokenOut)
async def login(body: LoginIn, db: DbDep, response: Response):
    user = await user_crud.get_by_email(db, body.email)
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    _set_refresh_cookie(response, user.id)
    return TokenOut(access_token=create_access_token(user.id))


@router.post("/refresh", response_model=TokenOut)
async def refresh(request: Request, db: DbDep, response: Response):
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    user_id = decode_token(token, "refresh") if token else None
    if user_id is None or await user_crud.get_by_id(db, user_id) is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
    _set_refresh_cookie(response, user_id)
    return TokenOut(access_token=create_access_token(user_id))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/auth")
