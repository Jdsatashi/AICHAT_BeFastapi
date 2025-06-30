from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Permission
from src.utils.perm_actions import actions_list


async def create_all_perms(model_name: str, obj_id=None, depend_on=None, db: AsyncSession = None) -> list[str]:
    """ Auto create permissions for the system. """
    all_perm_name = list()
    for action in actions_list:
        # Create permission name and description
        all_perm_name.append(get_perm_name(action, model_name, obj_id))
        if db is not None:
            perm = await generate_perm(model_name, action, obj_id, depend_on, db)
            db.add(perm)

    return all_perm_name


def get_perm_name(action: str, model_name: str, obj_id: int | None = None) -> str:
    """ Get permission name by action and model name. """
    if obj_id is not None:
        return f"{action}_{model_name}_{obj_id}"
    return f"{action}_{model_name}"


async def generate_perm(model_name: str, action: str, obj_id: int | None = None,
                        depend_on: str | None = None, db: AsyncSession = None) -> Permission:
    """ Create a single permission in the database. """
    perm_name = get_perm_name(action, model_name, obj_id)
    description = f"{action.upper()} permission on {model_name}"
    if obj_id is not None or obj_id != "":
        description = f"{description} for object ID {obj_id}"
    return Permission(
        name=perm_name,
        description=description,
        object_pk=obj_id,
        model_name=model_name,
        depend_on=depend_on if depend_on != '' else None
    )
