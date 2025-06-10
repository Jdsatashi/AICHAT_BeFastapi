from datetime import datetime

from jose import jwt, JWTError

from src.conf import settings
from src.schema.auth_schema import TokenPayload


def create_access_token(data: dict, expire) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "access"})
    
    # Save token to Redis
    
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: dict, expire) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> TokenPayload | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return TokenPayload(**payload)
    except JWTError:
        return None
