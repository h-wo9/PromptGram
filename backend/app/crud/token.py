from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import generate_refresh_token, hash_refresh_token
from app.models import RefreshToken


async def issue(db: AsyncSession, user_id: int) -> str:
    """새 refresh token 발급. 원문을 반환하고 DB에는 hash만 저장 (commit은 호출자가)."""
    token = generate_refresh_token()
    db.add(
        RefreshToken(
            user_id=user_id,
            token_hash=hash_refresh_token(token),
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
    )
    return token


async def get_valid(db: AsyncSession, token: str) -> RefreshToken | None:
    """hash 매칭 + 미만료 + 미revoked인 row 반환."""
    row = await db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(token))
    )
    if row is None or row.revoked:
        return None
    expires_at = row.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        return None
    return row
