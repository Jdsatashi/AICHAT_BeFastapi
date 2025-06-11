from typing import Optional, Generic, TypeVar, List

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel


# Schema for query parameters in various endpoints
class QueryParams(BaseModel):
    query: Optional[str] = Field(None, description="Search query string")
    page: int = Field(default=1, ge=1, description="Page number for pagination")
    limit: int = Field(default=10, ge=1, le=100, description="Number of items per page")
    order_by: Optional[str] = Field(None, description="Field to sort by")
    filter: Optional[str] = Field(None, description="Filter criteria in JSON format")
    strict: bool = Field(default=False, description="Whether to apply strict filtering")

    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "limit": 10
            }
        }


T = TypeVar("T")


class DataResponseModel(GenericModel, Generic[T]):
    data: List[T]
    total: int
    page: int
    limit: int

    class Config:
        orm_mode = True
