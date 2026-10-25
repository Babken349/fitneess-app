from datetime import datetime, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependency import get_db
from app.core.enums import UserRole
from app.auth.security import decode_token
from app.models.users import User
from app.repository import users as users_repository
from app.exceptions import ForbiddenError, EmailNotVerifiedError

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Wrong token type")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user = await users_repository.get_user_by_id(db, int(user_id))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenError()
    return current_user


async def require_premium(current_user: User = Depends(get_current_user)) -> User:
    now = datetime.now(timezone.utc)
    if not current_user.premium_until or now > current_user.premium_until:
        raise ForbiddenError()
    return current_user


async def require_verified(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_verified:
        raise EmailNotVerifiedError()
    return current_user


async def require_researcher_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role not in (UserRole.RESEARCHER, UserRole.ADMIN):
        raise ForbiddenError()
    return current_user