# src/dependencies/auth.py
from typing import Set

from fastapi import Request, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.services.auth_services import check_access_token

EXEMPT_PATHS: Set[str] = {
    "/",
    "/comepass/api/v1/auth/login",
    "/comepass/api/v1/auth/refresh-token",
    "/comepass/api/v1/auth/check-access"
}


async def user_auth(
        request: Request,
        db: AsyncSession = Depends(get_db)
) -> None:
    path = request.url.path
    if path in EXEMPT_PATHS:
        return  # bypass auth cho public endpoints

    # Get header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ", 1)[1]
    # Validate token
    data = await check_access_token(token, db)

    if data is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="error access token: " + data,
            headers={"WWW-Authenticate": "Bearer"},
        )
