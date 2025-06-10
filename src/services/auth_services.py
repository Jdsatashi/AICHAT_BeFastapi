from datetime import timedelta, datetime
from typing import Any, Type

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import settings
from src.db.redisdb import redis_client, store_token
from src.handlers.check_email import is_valid_email
from src.handlers.jwt_token import create_refresh_token, create_access_token, decode_token
from src.models.auth import RefreshToken
from src.models.users import Users
from src.schema.auth_schema import LoginForm, TokenPayload
from src.utils.constant import not_found, not_active, pw_not_match, token_not_found, token_not_active, token_expired, \
    token_invalid
from src.utils.rand_str import random_string
from src.utils.unow import now_vn


async def login(db: AsyncSession, user_data: LoginForm) -> dict[str, str | Type[Users]] | str:
    # App allow login with either username or email
    # Get username field to check if it is an email or username
    username = user_data.username
    check_email = is_valid_email(username)

    # Query user based on username or email
    if check_email:
        user = await db.execute(
            select(Users).where(Users.email == username)
        )
    else:
        user = await db.execute(
            select(Users).where(Users.username == username)
        )

    # Get first result from query
    user = user.scalars().first()

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
    seconds_expire = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

    # Create refresh tokens
    refresh_token = create_refresh_token(token_data, refresh_expire)
    try:
        # Save refresh token to database
        new_rf = await save_refresh_token(db, user.id, refresh_token, refresh_expire)
    except IntegrityError as e:
        # Handle IntegrityError if the refresh token already exists
        token_data["otp"] = random_string(8)
        refresh_token = create_refresh_token(token_data, refresh_expire)
        new_rf = await save_refresh_token(db, user.id, refresh_token, refresh_expire)

    # Create access token
    token_data["refresh_id"] = new_rf.id
    access_token = create_access_token(token_data, access_expire)
    # Check if access token is created successfully
    await redis_client.set(f"{store_token}:{new_rf.id}", access_token, ex=seconds_expire)

    # Response structure data
    return {
        "user": user,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


# Save Refresh Token to database
async def save_refresh_token(db: AsyncSession, user_id: int, refresh_token: str,
                             expiration: Any) -> RefreshToken | None:
    try:
        # Create a new RefreshToken instance
        new_refresh_token = RefreshToken(
            refresh_token=refresh_token,
            user_id=user_id,
            expiration=expiration
        )
        # Add the new refresh token to the database session
        db.add(new_refresh_token)
        await db.commit()
        # Refresh the instance to get the ID and other fields
        await db.refresh(new_refresh_token)
        return new_refresh_token
    except IntegrityError as e:
        # Handle IntegrityError if the refresh token already exists
        await db.rollback()
        raise e


# Refresh new access token using refresh token
async def refresh_access_token(db: AsyncSession, refresh_token: str) -> str | None:
    # Check if the refresh token is valid
    token = await check_refresh_token(db, refresh_token)
    if isinstance(token, str):
        return token

    # Prepare data for new access token
    token_data = {"user_id": token.user_id, "refresh_id": token.id}
    access_expire = now_vn() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    seconds_expire = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

    # Create new access token
    new_access_token = create_access_token(token_data, access_expire)
    await redis_client.set(f"{store_token}:{token.id}", new_access_token, ex=seconds_expire)

    return new_access_token


# Check if refresh token valid
async def check_refresh_token(db: AsyncSession, refresh_token: str | int) -> RefreshToken | str:
    if isinstance(refresh_token, int):
        # If refresh_token is an integer, it's the token ID
        token = await db.execute(
            select(RefreshToken)
            .where(RefreshToken.id == refresh_token)
        )
    else:
        # If refresh_token is a string, it's the token value
        token = await db.execute(
            select(RefreshToken)
            .where(RefreshToken.refresh_token == refresh_token)
        )
    token = token.scalar_one_or_none()
    # Check if token exists and is active
    if not token:
        return token_not_found
    elif not token.is_active:
        return token_not_active
    elif token.expiration <= now_vn():
        return token_expired
    return token


# Check if access token valid
async def check_access_token(access_token: str, db: AsyncSession) -> str | None:
    # Decode the access token
    token_decoded: TokenPayload = decode_token(access_token)

    # Check if token is decoded successfully
    if not token_decoded:
        return token_invalid

    # Check if token type is expired
    expired_at = token_decoded.exp
    exp_datetime = datetime.fromtimestamp(expired_at).replace(tzinfo=None)
    if exp_datetime < now_vn():
        return token_expired

    # Check if refresh_id exists in the token
    refresh = await check_refresh_token(db, int(token_decoded.refresh_id))
    if isinstance(refresh, str):
        return f"refresh_{refresh}"

    # Check if access token exists in Redis
    redis_token = await redis_client.get(f"{store_token}:{token_decoded.refresh_id}")
    if not redis_token or access_token != redis_token:
        return token_not_found

    return None
