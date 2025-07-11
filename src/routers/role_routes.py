from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.models import Role
from src.schema.queries_params_schema import QueryParams, DataResponseModel
from src.schema.role_schema import RoleOutput, RoleCreate
from src.services.generic_services import get_all
from src.services.role_services import create_role
from src.utils.api_path import RoutePaths

role_router = APIRouter(prefix=RoutePaths.Role.init, tags=["Roles"])


@role_router.get(path=RoutePaths.Role.list, response_model=DataResponseModel[RoleOutput])
async def list_roles(db: AsyncSession = Depends(get_db), params: QueryParams = Depends()):
    roles = await get_all(db, Role, params)
    return roles

@role_router.post(path=RoutePaths.Role.add, response_model=RoleOutput)
async def add_role(role: RoleCreate, db: AsyncSession = Depends(get_db)):
    """Create a new role."""
    new_role = await create_role(db, role)
    return new_role
