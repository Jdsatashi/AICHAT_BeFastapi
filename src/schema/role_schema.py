from pydantic import BaseModel


class RoleOutput(BaseModel):
    id: int
    name: str
    description: str | None = None
    is_active: bool
    group: bool = False
    
    class Config:
        orm_mode = True
        
        
class RoleCreate(BaseModel):        
    name: str
    description: str | None = None
    is_active: bool = True
    group: bool = False
    
    class Config:
        orm_mode = True
