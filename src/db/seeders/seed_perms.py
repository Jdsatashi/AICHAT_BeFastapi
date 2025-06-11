import asyncio
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import AsyncSessionLocal
from src.models import Permission, Role, MODEL_REGISTRY
from src.utils.perm_actions import actions_list, actions


async def seed_permissions():
    async with AsyncSessionLocal() as db:  # type: AsyncSession
        # 1. Generate permissions
        for model_name in MODEL_REGISTRY:
            for action in actions_list:
                name = f"{action}_{model_name}"
                description = f"{action.upper()} permission on {model_name}"
                db.add(Permission(
                    name=name,
                    description=description,
                    created_at=datetime.now()
                ))
        await db.commit()

        # 2. Reload all permissions just created
        result = await db.execute(select(Permission))
        all_perms = result.scalars().all()

        # 3. Create roles
        admin = Role(name="admin", description="Administrator role", is_active=True)
        manager = Role(name="manager", description="Manager role", is_active=True)
        staff = Role(name="staff", description="Staff role", is_active=True)
        
        # 4. Assign permissions to roles
        # Admin: all_*
        admin.permissions = [p for p in all_perms if p.name.startswith(actions.all)]
        # Manager: read_* và actions_*
        manager.permissions = [p for p in all_perms if p.name.startswith((actions.read, actions.actions))]
        # Staff: only read_*
        # staff.permissions = [p for p in all_perms if p.name.startswith("read_")]

        db.add_all([admin, manager, staff])
        await db.commit()
        print("✅ Seed permissions and roles success!")


if __name__ == "__main__":
    asyncio.run(seed_permissions())
