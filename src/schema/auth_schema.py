from typing import Literal

from pydantic import BaseModel

from src.schema.user_schema import UserOutput


class LoginRequest(BaseModel):
    username: str = None
    password: str = None


class LoginOutput(BaseModel):
    user: UserOutput
    access_token: str
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AccessTokenRequest(BaseModel):
    access_token: str


class CheckRoleRequest(BaseModel):
    role: str


# Token payloads for access/refresh tokens
class TokenPayload(BaseModel):
    user_id: int
    refresh_id: int | None = None
    exp: int
    type: Literal["access", "refresh"]
