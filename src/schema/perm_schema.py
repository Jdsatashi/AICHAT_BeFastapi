from typing import Optional, List, ClassVar

from pydantic import BaseModel, field_validator

from src.utils.perm_actions import actions_list


class AddPemRequest(BaseModel):
    description: Optional[str] = None
    action: Optional[str] = None
    object_pk: Optional[str] = None
    model_name: Optional[str] = None

    _actions_list: ClassVar[List[str]] = actions_list

    @field_validator("action")
    def validate_action(cls, v):
        if v is not None and v not in cls._actions_list:
            raise ValueError(f"action must be one of {cls._actions_list}")
        return v
    
    class Config:
        extra = "forbid"
    