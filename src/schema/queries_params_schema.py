from pydantic import BaseModel, Field


# Schema for query parameters in various endpoints
class QueryParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number for pagination")
    limit: int = Field(default=10, ge=1, le=100, description="Number of items per page")
    sort_by: str | None = Field(default=None, description="Field to sort by")
    sort_order: str = Field(default="asc", description="Sort order: 'asc' or 'desc'")
    
    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "limit": 10
            }
        }