from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Role
from src.schema.queries_params_schema import QueryParams
from src.schema.role_schema import RoleCreate
from src.services.generic_services import get_all


async def get_roles(db: AsyncSession, params: QueryParams):
    """ Fetch all roles with optional query parameters."""
    roles = await get_all(db, Role, params)
    return roles


async def create_role(db: AsyncSession, role_data: RoleCreate):
    """ Create a new role in the database."""
    new_role = Role(
        name=role_data.name,
        description=role_data.description,
        permissions=role_data.permissions,
        group=role_data.group,
    )
    db.add(new_role)
    await db.commit()
    await db.refresh(new_role)
    return new_role
