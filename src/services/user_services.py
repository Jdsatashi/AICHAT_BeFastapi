from typing import Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.handlers.pw_hash import hash_pass
from src.models.users import Users
from src.schema.user_schema import UserCreate, UserSelfUpdate, ChangePassword
from src.utils.constant import pw_wrong, pw_not_match


async def get_all_users(db: AsyncSession):
    result = await db.execute(select(Users))
    return result.scalars().all()


async def create_user(db: AsyncSession, user_data: UserCreate) -> Users:
    password = hash_pass(user_data.password)

    db_user = Users(
        username=user_data.username,
        email=str(user_data.email),
        password=password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_id(db: AsyncSession, user_id: int) -> Type[Users] | None:
    user = await db.get(Users, user_id)
    return user


async def update_user_self(db: AsyncSession, user_id: int, user_data: UserSelfUpdate) -> Type[Users] | None:
    user = await db.get(Users, user_id)
    if not user:
        return None

    if user_data.username:
        user.username = user_data.username
    if user_data.email:
        user.email = str(user_data.email)

    await db.commit()
    await db.refresh(user)
    return user


async def destroy_user(db: AsyncSession, user_id: int) -> bool | None:
    user = await db.get(Users, user_id)
    if not user:
        return None
    try:
        await db.delete(user)
        await db.commit()

        return True
    except Exception as e:
        await db.rollback()
        print(f"Error deleting user: {e}")
        return False


async def change_password(db: AsyncSession, user_id: int, user_data: ChangePassword) -> str | None | bool:
    user = await db.get(Users, user_id)
    if not user:
        return None
    # check_pw = verify_password(user_data.old_password, user.password)
    if not user.check_pw(pw=user_data.old_password):
        return pw_wrong

    if user_data.new_password != user_data.confirm_new_password:
        return pw_not_match

    user.password = hash_pass(user_data.new_password)
    await db.commit()
    await db.refresh(user)
    return True
