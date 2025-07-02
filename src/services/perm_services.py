from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from src.handlers.perm import get_perm_name
from src.models import Permission, MODEL_REGISTRY
from src.schema.perm_schema import AddPemRequest
from src.schema.queries_params_schema import QueryParams
from src.services.generic_services import get_all
from src.utils.perm_actions import actions_main, actions


async def get_perms(db: AsyncSession, params: QueryParams):
    return await get_all(db, Permission, params)


async def create_perm(db: AsyncSession, perm_data: AddPemRequest) -> Permission | str:
    """ Create a new permission in the database."""
    is_valid, err = validate_perm_data(db, perm_data)
    if not is_valid:
        return err
    # Generate permission name based on action, model name, and option object primary key.
    perm_name = f"{perm_data.action}_{perm_data.model_name}"
    if perm_data.object_pk:
        perm_name += f"_{perm_data.object_pk}"

    # Check if the permission already exists
    result = await db.execute(select(exists().where(Permission.name == perm_name)))
    # If the permission already exists, return an error message
    if result.scalar():
        return f"Permission {perm_name} already exists."

    # Create a new permission
    new_perm = Permission(
        name=perm_name,
        description=perm_data.description,
        action=perm_data.action,
        object_pk=perm_data.object_pk,
        model_name=perm_data.model_name
    )

    db.add(new_perm)
    # Commit changes and refresh data
    await db.commit()
    await db.refresh(new_perm)
    return new_perm


async def validate_perm_data(db: AsyncSession, perm_data: AddPemRequest) -> tuple[bool, str | None]:
    """ Validate the permission data before creating a new permission."""
    model_name = perm_data.model_name
    # Check if models String is valid
    if model_name not in list(MODEL_REGISTRY.keys()):
        return False, f"Model {model_name} does not exist in the registry."
    # Check primary key of the model
    if perm_data.object_pk:
        # Get models class
        model = MODEL_REGISTRY[model_name]
        obj = await db.get(model, perm_data.object_pk)
        # Check if the model has the primary key specified
        if obj is None:
            return False, f"Model {model_name} does not have a primary key named {perm_data.object_pk}."
    return True, None


async def create_main_perms(db: AsyncSession, model_name: str, obj_id: int) -> list[Permission]:
    """ Create main permissions for all models in the registry."""
    permissions = []
    for action in actions_main:
        perm_name = get_perm_name(model_name, action, obj_id)
        perm = Permission(
            name=perm_name,
            description=f"{action.capitalize()} permission for object pk {obj_id}",
            object_pk=obj_id,
            model_name="Users",
        )
        db.add(perm)
        if action != actions.destroy:
            permissions.append(perm)
    return permissions
