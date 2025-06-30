from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Permission
from src.utils.perm_actions import actions_list


async def auto_create_perms(model_name, obj_id = None, db: AsyncSession = None) -> list[str]:
    """ Auto create permissions for the system. """
    all_perm_name = list()
    for action in actions_list:
        # Create permission name and description
        name = f"{action}_{model_name}"
        all_perm_name.append(name)
        description = f"{action.upper()} permission on {model_name}"
        if obj_id is not None:
            name = f"{name}_{obj_id}"
            description = f"{description} for object ID {obj_id}"
        if db is not None:
            try:
                db.add(Permission(
                    name=name,
                    description=description,
                    model_name=model_name,
                ))
                # Apply the changes to the database
                await db.commit()
            except Exception as e:
                await db.rollback()
                raise e
    return all_perm_name
