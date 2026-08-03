from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.enums import UserRole
from app.core.dependency import get_db
from app.auth.security import decode_token
from app.models.users import User
from app.repository import users as users_repository
from app.exceptions import ForbiddenError, EmailNotVerifiedError
from datetime import datetime, timezone
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Wrong token type")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user = users_repository.get_user_by_id(db, int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenError()

    return current_user

def require_premium(current_user: User = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    if not current_user.premium_until or now > current_user.premium_until:
        raise ForbiddenError()
    return current_user

def require_verified(current_user: User = Depends(get_current_user)):
    if not current_user.is_verified:
        raise EmailNotVerifiedError()
    return current_user