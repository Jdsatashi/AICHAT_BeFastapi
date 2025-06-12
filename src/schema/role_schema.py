from pydantic import BaseModel


class RoleOutput(BaseModel):
    id: int
    name: str
    description: str | None = None
    is_active: bool
    
    class Config:
        orm_mode = True