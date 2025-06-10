from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.cores.auth_schema import LoginForm, LoginResponse, RefreshTokenRequest, AccessTokenRequest
from src.db.database import get_db
from src.services.auth_services import login, check_access_token
from src.utils.constant import token_not_found, token_not_active, token_expired

auth_router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="authenticate")

@auth_router.post("/login", response_model=LoginResponse)
def user_login(auth_data: LoginForm, db: Session = Depends(get_db)):
    result = login(db, auth_data)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    return result

@auth_router.post("/refresh-token")
def refresh_access_token(refresh_token: RefreshTokenRequest, db: Session = Depends(get_db)):
    from src.services.auth_services import refresh_access_token
    rf_token = refresh_token.refresh_token
    # Refresh the access token
    new_access_token = refresh_access_token(db, rf_token)
    if new_access_token in [token_not_found, token_not_active ,token_expired]:
        raise HTTPException(status_code=400, detail=new_access_token)

    return {"access_token": new_access_token}


@auth_router.post("/check-access")
def access_token_checking(token: AccessTokenRequest, db: Session = Depends(get_db)):
    # Check if the access token is valid
    is_valid = check_access_token(token.access_token, db)
    if isinstance(is_valid, str):
        raise HTTPException(status_code=400, detail=is_valid)
    return {"detail": "Access token is valid"}


@auth_router.get("/check-access")
def access_token_checking(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    # Check if the access token is valid
    is_valid = check_access_token(token, db)
    if isinstance(is_valid, str):
        raise HTTPException(status_code=400, detail=is_valid)
    return {"detail": "Access token is valid"}