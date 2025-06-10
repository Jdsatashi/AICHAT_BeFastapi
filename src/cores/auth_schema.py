from pydantic import BaseModel

from src.cores.user_schema import UserOut


class LoginForm(BaseModel):
    username: str = None
    password: str = None
    
    
class LoginResponse(BaseModel):
    user: UserOut
    access_token: str
    refresh_token: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str
