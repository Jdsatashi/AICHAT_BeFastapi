from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.schema.auth_schema import LoginRequest, LoginOutput, RefreshTokenRequest, AccessTokenRequest
from src.services.auth_services import login, check_access_token
from src.utils.err_msg import err_code

auth_router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="authenticate")


@auth_router.post("/login", response_model=LoginOutput)
async def user_login(auth_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """" Login user with username or email and password """
    result = await login(db, auth_data)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    return result


@auth_router.post("/refresh-token")
async def refresh_access_token(rf_token: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    from src.services.auth_services import refresh_access_token
    # Refresh the access token
    new_access_token = await refresh_access_token(db, rf_token.refresh_token)
    if new_access_token in list(err_code.keys()):
        raise HTTPException(status_code=400, detail="refresh token " + new_access_token)

    return {"access_token": new_access_token}


@auth_router.post("/check-access")
async def access_token_checking(token: AccessTokenRequest, db: AsyncSession = Depends(get_db)):
    """ Check if the access token is valid with token in request body """
    is_valid = await check_access_token(token.access_token, db)
    if isinstance(is_valid, str):
        raise HTTPException(status_code=400, detail="error access token: " + is_valid)
    return {"detail": "Access token is valid"}


@auth_router.get("/check-access")
async def access_token_checking(token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)):
    """ Check if the access token is valid with token in request header """
    is_valid = await check_access_token(token, db)
    if isinstance(is_valid, str):
        raise HTTPException(status_code=400, detail="error access token: " + is_valid)
    return {"detail": "Access token is valid"}
