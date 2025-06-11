from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Permission

async def get_all_perms(db: AsyncSession):
    perms = await db.execute(select(Permission))
    return perms.scalars().all()
    