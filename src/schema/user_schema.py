from pydantic import BaseModel, EmailStr
from datetime import datetime

# Schema create users (request)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str
    

# User self update schema (request)
class UserSelfUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None

    class Config:
        extra = "forbid"


# User self change password schema (request)
class ChangePassword(BaseModel):
    old_password: str
    new_password: str
    confirm_new_password: str

    class Config:
        extra = "forbid"


# Schema return json (response)
class UserOutput(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
