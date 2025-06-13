from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession

from src.handlers.pw_hash import hash_pass
from src.models.users import Users
from src.schema.queries_params_schema import QueryParams
from src.schema.user_schema import UserCreate, UserSelfUpdate, ChangePassword
from src.services.generic_services import get_all
from src.utils.err_msg import err_msg


async def get_users(db: AsyncSession, params: QueryParams):
    return await get_all(db, Users, params)


async def create_user(db: AsyncSession, user_data: UserCreate) -> Users:
    """ Function create new user with username, email and password """
    # Get password to hash
    password = hash_pass(user_data.password)
    # Init Users object
    new_user = Users(
        username=user_data.username,
        email=str(user_data.email),
        password=password
    )
    # Assign add user to db
    db.add(new_user)
    # Commit change to db
    await db.commit()
    # Refresh to get new object with id in db
    await db.refresh(new_user)
    return new_user


async def get_user(db: AsyncSession, user_id: int) -> Type[Users] | None:
    """ Function get specific user by id """
    return await db.get(Users, user_id)


async def update_user(db: AsyncSession, user_id: int, user_data: UserSelfUpdate) -> Type[Users] | None:
    """ Function update user email or username """
    # Check if user exist
    user = await db.get(Users, user_id)
    if not user:
        return err_msg.not_found
    # Assign new username if inputted
    if user_data.username:
        user.username = user_data.username
    # Assign new email if inputted
    if user_data.email:
        user.email = str(user_data.email)
    # Commit change to db
    await db.commit()
    # Refresh to get new update of user
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> None | str:
    """ Function delete user """
    # Check if user exist
    user = await db.get(Users, user_id)
    if not user:
        return err_msg.not_found
    # Handle try to delete user
    await db.delete(user)
    await db.commit()

    return None


async def change_password(db: AsyncSession, user_id: int, user_data: ChangePassword) -> str | None:
    """ Function for user change their password """
    # Get user by id
    user = await db.get(Users, user_id)
    # Check if user existed
    if not user:
        return err_msg.not_found

    # Validate input current password
    if not user.check_pw(pw=user_data.old_password):
        return err_msg.pw_wrong

    # Validate new password and confirm password
    if user_data.new_password != user_data.confirm_new_password:
        return err_msg.pw_not_match

    # Hash new password and assign to user object
    user.password = hash_pass(user_data.new_password)

    # Commit change
    await db.commit()
    # Refresh to get newest data of object user
    await db.refresh(user)
    # Return None if not error
    return None
