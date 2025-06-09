from typing import Any, Type

from sqlalchemy.orm import Session

from src.cores.auth_schema import LoginForm, LoginResponse
from src.cores.user_schema import UserOut
from src.handlers.check_email import is_valid_email
from src.handlers.jwt_token import create_refresh_token, create_access_token
from src.models.users import Users
from src.utils.constant import not_found, not_active, pw_not_match


def login(db: Session, user_data: LoginForm) -> dict[str, str | Type[Users]] | str:
    username = user_data.username
    check_email = is_valid_email(username)
    if check_email:
        user = db.query(Users).filter(Users.email == username).first()
    else:
        user = db.query(Users).filter(Users.username == username).first()
    
    if not user:
        return not_found
    
    if not user.is_active:
        return not_active
    
    if not user.check_pw(pw=user_data.password):
        return pw_not_match
    
    token_data = {"user_id": user.id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    response = {
        "user": user,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
    return response
