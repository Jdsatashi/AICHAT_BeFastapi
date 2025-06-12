from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.models import Role
from src.schema.queries_params_schema import QueryParams, DataResponseModel
from src.schema.role_schema import RoleOutput
from src.services.generic_services import get_all

role_router = APIRouter(prefix="/roles", tags=["Roles"])


@role_router.get("/", response_model=DataResponseModel[RoleOutput])
async def get_roles(db: AsyncSession = Depends(get_db), params: QueryParams = Depends()):
    roles = await get_all(db, Role, params)
    return roles

# @role_router.post("/", response_model=RoleOutput)
# async def 