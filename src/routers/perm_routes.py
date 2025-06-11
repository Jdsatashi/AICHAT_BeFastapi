from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db

perm_router = APIRouter(prefix="/perms", tags=["Permissions"])


@perm_router.get("/")
async def get_permissions(db: AsyncSession = Depends(get_db)):
    perms = await get_all_perms(db)
    # Placeholder for the actual implementation
    return {"message": "This is a placeholder for permissions endpoint."}