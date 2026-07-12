from fastapi import APIRouter, HTTPException, status

from app.api.deps import DbDep
from app.core.security import create_access_token, hash_password, verify_password
from app.crud import token as token_crud
from app.crud import user as user_crud
from app.schemas.user import LoginIn, RefreshIn, SignupIn, TokenPairOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


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


@router.post("/login", response_model=TokenPairOut)
async def login(body: LoginIn, db: DbDep):
    user = await user_crud.get_by_email(db, body.email)
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    refresh = await token_crud.issue(db, user.id)
    await db.commit()
    return TokenPairOut(access_token=create_access_token(user.id), refresh_token=refresh)


@router.post("/refresh", response_model=TokenPairOut)
async def refresh(body: RefreshIn, db: DbDep):
    """rotation: 유효한 refresh를 revoke하고 새 pair 발급. 재사용·무효 토큰은 401."""
    row = await token_crud.get_valid(db, body.refresh_token)
    if row is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
    row.revoked = True
    new_refresh = await token_crud.issue(db, row.user_id)
    await db.commit()
    return TokenPairOut(
        access_token=create_access_token(row.user_id), refresh_token=new_refresh
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: RefreshIn, db: DbDep):
    row = await token_crud.get_valid(db, body.refresh_token)
    if row is not None:
        row.revoked = True
        await db.commit()
