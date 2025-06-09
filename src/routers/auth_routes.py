from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.cores.auth_schema import LoginForm, LoginResponse
from src.db.database import get_db
from src.services.auth_services import login

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login", response_model=LoginResponse)
def user_login(auth_data: LoginForm, db: Session = Depends(get_db)):
    result = login(db, auth_data)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    return result
