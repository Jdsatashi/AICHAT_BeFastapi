from pydantic import EmailStr, ValidationError
from pydantic_core import PydanticCustomError


def is_valid_email(email: str) -> bool:
    try:
        EmailStr._validate(email)
        return True
    except (ValidationError, PydanticCustomError):
        return False
