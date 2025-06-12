from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.schema.queries_params_schema import QueryParams, DataResponseModel
from src.services.perm_services import get_perms

perm_router = APIRouter(prefix="/perms", tags=["Permissions"])


@perm_router.get("/", response_model=DataResponseModel)
async def list_perms(db: AsyncSession = Depends(get_db), params: QueryParams = Depends(QueryParams)):
    perms = await get_perms(db, params)
    # Placeholder for the actual implementation
    return perms
