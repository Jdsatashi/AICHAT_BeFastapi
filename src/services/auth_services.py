from datetime import timedelta
from typing import Any, Type

from sqlalchemy.orm import Session

from src.conf import settings
from src.cores.auth_schema import LoginForm
from src.handlers.check_email import is_valid_email
from src.handlers.jwt_token import create_refresh_token, create_access_token
from src.models.auth import RefreshToken
from src.models.users import Users
from src.utils.constant import not_found, not_active, pw_not_match, token_not_found, token_not_active, token_expired
from src.utils.unow import now_vn


def login(db: Session, user_data: LoginForm) -> dict[str, str | Type[Users]] | str:
    # App allow login with either username or email
    # Get username field to check if it is an email or username
    username = user_data.username
    check_email = is_valid_email(username)

    # Query user based on username or email
    if check_email:
        user = db.query(Users).filter(Users.email == username).first()
    else:
        user = db.query(Users).filter(Users.username == username).first()

    # Check if user exists
    if not user:
        return not_found

    # Check if user is active
    if not user.is_active:
        return not_active

    # Check if password matches
    if not user.check_pw(pw=user_data.password):
        return pw_not_match

    # Prepare tokens data
    token_data = {"user_id": user.id}
    access_expire = now_vn() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expire = now_vn() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAY)

    # Create access and refresh tokens
    access_token = create_access_token(token_data, access_expire)
    refresh_token = create_refresh_token(token_data, refresh_expire)

    # Save refresh token to database
    save_refresh_token(db, user.id, refresh_token, refresh_expire)

    # Response structure data
    return {
        "user": user,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


# Save Refresh Token to database
def save_refresh_token(db: Session, user_id: int, refresh_token: str, expiration: Any) -> None:
    new_refresh_token = RefreshToken(
        refresh_token=refresh_token,
        user_id=user_id,
        expiration=expiration
    )
    db.add(new_refresh_token)
    db.commit()
    db.refresh(new_refresh_token)
    
    
# Refresh new access token using refresh token
def refresh_access_token(db: Session, refresh_token: str) -> str | None:
    # Check if the refresh token is valid
    token = check_refresh_token(db, refresh_token)
    if isinstance(token, str):
        return token

    # Create new access token
    token_data = {"user_id": token.user_id}
    access_expire = now_vn() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(token_data, access_expire)

    return new_access_token


# Check if refresh token valid
def check_refresh_token(db: Session, refresh_token: str) -> RefreshToken | str:
    token = db.query(RefreshToken).filter(RefreshToken.refresh_token == refresh_token).first() 
    if not token:
        return token_not_found
    elif not token.is_active:
        return token_not_active
    elif token.expiration <= now_vn():
        return token_expired
    return token