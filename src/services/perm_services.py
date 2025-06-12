from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Permission, MODEL_REGISTRY
from src.schema.perm_schema import AddPemRequest
from src.schema.queries_params_schema import QueryParams
from src.services.generic_services import get_all


async def get_perms(db: AsyncSession, params: QueryParams):
    return await get_all(db, Permission, params)


async def create_perm(db: AsyncSession, perm_data: AddPemRequest) -> Permission | str:
    is_valid, err = validate_perm_data(perm_data)
    if not is_valid:
        return err
    perm_name = f"{perm_data.action}_{perm_data.model_name}"
    if perm_data.object_pk:
        perm_name += f"_{perm_data.object_pk}"
    result = await db.execute(select(exists().where(Permission.name == perm_name)))

    if result.scalar():
        return f"Permission {perm_name} already exists."
    new_perm = Permission(
        name=perm_name,
        description=perm_data.description,
        action=perm_data.action,
        object_pk=perm_data.object_pk,
        model_name=perm_data.model_name
    )
    db.add(new_perm)
    await db.commit()
    await db.refresh(new_perm)
    return new_perm


async def validate_perm_data(db: AsyncSession, perm_data: AddPemRequest) -> tuple[bool, str | None]:
    # Check if models String is valid
    if perm_data.model_name not in list(MODEL_REGISTRY.keys()):
        return False, f"Model {perm_data.model_name} does not exist in the registry."
    # Check primary key of the model
    if perm_data.object_pk:
        # Get models class
        model = MODEL_REGISTRY[perm_data.model_name]
        obj = await db.get(model, perm_data.object_pk)
        # Check if the model has the primary key specified
        if obj is None:
            return False, f"Model {perm_data.model_name} does not have a primary key named {perm_data.object_pk}."
    return True, None
