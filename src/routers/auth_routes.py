from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.cores.auth_schema import LoginForm, LoginResponse, RefreshTokenRequest
from src.db.database import get_db
from src.services.auth_services import login
from src.utils.constant import token_not_found, token_not_active, token_expired

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


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