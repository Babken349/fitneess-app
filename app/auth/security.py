from datetime import datetime, timedelta, timezone
import uuid
import jwt
from fastapi import HTTPException, status
from app.core.config import settings

def create_access_token(*, user_id: int, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    
    payload = {
        "sub": str(user_id),
        "type": "access",
        "role": role,
        "exp": expire,
    }
    
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(*, user_id: int) -> tuple[str, str, datetime]:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Уникальный ID токена для базы данных (чтобы мы могли его отозвать/проверить)
    jti = str(uuid.uuid4())
    
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": jti,
        "exp": expire,
    }
    
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, jti, expire


def decode_token(token: str) -> dict:
    """Расшифровывает любой токен. Кидает 401, если токен протух или поддельный.
        if/else проверяет ожидаемые состояния программы.
        try/except перехватывает исключения (Exceptions), которые были вызваны где-то внутри."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")