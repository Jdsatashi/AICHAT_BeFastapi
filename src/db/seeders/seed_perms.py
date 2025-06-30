import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.conf.settings import ADMIN_PASSWORD, ADMIN_EMAIL
from src.db.database import AsyncSessionLocal
from src.handlers.perm import auto_create_perms
from src.handlers.pw_hash import hash_pass
from src.models import Permission, Role, MODEL_REGISTRY, Users
from src.utils.perm_actions import actions_list, actions
from src.utils.user_roles import UserRole


async def seed_permissions():
    """ Seeding default permissions and roles into the database. """
    async with AsyncSessionLocal() as db:  # type: AsyncSession
        try:
            # Process create permission base on models
            await create_model_perms(db)
            # Process create default roles with permissions
            await create_role_default(db)
            print("✅ Seed permissions and roles success!")
        except Exception as e:
            print(f"❌ Error seeding permissions and roles: {e}")
            raise e


async def create_admin_perms():
    """ Create admin user with admin permissions if not exists. """
    async with AsyncSessionLocal() as db:  # type: AsyncSession
        try:
            # Check if admin user already exists
            result = await db.execute(select(Users)
                                      .options(selectinload(Users.roles))
                                      .where(Users.username == UserRole.ADMIN))
            user = result.scalars().first()
            # If user does not exist, create it
            if not user:
                db.add(Users(
                    username=UserRole.ADMIN,
                    email=ADMIN_EMAIL,
                    password=hash_pass(ADMIN_PASSWORD),
                    is_active=True
                ))
                # Commit the new user to the database
                await db.commit()
                # Refresh the session to get the new user
                await db.flush()
                # Re-fetch the user to ensure we have the latest state
                result = await db.execute(select(Users)
                                          .options(selectinload(Users.roles))
                                          .where(Users.username == UserRole.ADMIN))
                user = result.scalars().first()
            # Get the admin role
            admin = await db.execute(select(Role).where(Role.name == UserRole.ADMIN))
            admin_role = admin.scalars().first()
            # Add role to admin user
            user.roles = [admin_role]
            await db.commit()
            print("✅ Create admin permissions successfully!")
        except Exception as e:
            await db.rollback()
            print(f"❌ Error creating admin permissions: {e}")
            raise e


async def create_model_perms(db: AsyncSession):
    """ Create permissions for each model in the MODEL_REGISTRY. """
    try:
        # Loop to each model in the MODEL_REGISTRY
        for model_name in MODEL_REGISTRY:
            await auto_create_perms(model_name, db=db)
    except Exception as e:
        await db.rollback()
        print(f"❌ Error creating model permissions: {e}")
        raise e


async def create_role_default(db: AsyncSession):
    """ Create default roles with permissions. """
    try:
        # Reload all permissions just created
        result = await db.execute(select(Permission))
        all_perms = result.scalars().all()

        # Create default roles
        admin = Role(name=UserRole.ADMIN, description="Administrator role", is_active=True, group=True)
        manager = Role(name=UserRole.MANAGER, description="Manager role", is_active=True, group=True)
        staff = Role(name=UserRole.STAFF, description="Staff role", is_active=True, group=True)
        draft = Role(name=UserRole.DRAFT, description="Draft role for tester", is_active=True, group=True)

        # Assign permissions to roles
        # Admin: all_*
        admin.permissions = [p for p in all_perms if p.name.startswith(actions.all)]
        # Manager: read_* và actions_*
        manager.permissions = [p for p in all_perms if p.name.startswith((actions.read, actions.add, actions.edit))]
        # Staff: only read_*
        # staff.permissions = [p for p in all_perms if p.name.startswith("read_")]

        db.add_all([admin, manager, staff, draft])
        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"❌ Error creating default roles: {e}")
        raise e


if __name__ == "__main__":
    asyncio.run(seed_permissions())
    asyncio.run(create_admin_perms())
