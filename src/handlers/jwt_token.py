from datetime import datetime, timedelta

from jose import jwt, JWTError

from src.conf import settings
from src.schema.auth_schema import TokenPayload
from src.utils.unow import now_vn


def create_access_token(data: dict, expire = None) -> str:
    if expire is None:
        expire = now_vn() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "access"})
    
    # Save token to Redis
    
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: dict, expire = None) -> str:
    if expire is None:
        expire = now_vn() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAY)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> TokenPayload | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return TokenPayload(**payload)
    except JWTError:
        return None
