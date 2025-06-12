from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.schema.queries_params_schema import QueryParams, DataResponseModel
from src.schema.user_schema import UserCreate, UserOutput, UserSelfUpdate, ChangePassword
from src.services.user_services import get_users, create_user, get_user, update_user, delete_user, change_password
from src.utils.constant import pw_wrong, pw_not_match

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get("/", response_model=DataResponseModel[UserOutput])
async def list_user(params: QueryParams = Depends(), db: AsyncSession = Depends(get_db)):
    users = await get_users(db, params)
    return users


@user_router.post("/", response_model=UserOutput, status_code=status.HTTP_201_CREATED)
async def add_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user)


@user_router.get("/{user_id}", response_model=UserOutput)
async def retrieve_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.put("/{user_id}", response_model=UserOutput)
async def edit_user(user_id: int, user_data: UserSelfUpdate, db: AsyncSession = Depends(get_db)):
    user = await update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await delete_user(db, user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    elif not result:
        raise HTTPException(status_code=500, detail="Error deleting user")
    return {"detail": "User deleted successfully"}


@user_router.put("/{user_id}/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password_user(user_id: int, change_data: ChangePassword, db: AsyncSession = Depends(get_db)):
    user = await change_password(db, user_id, change_data)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    elif user == pw_wrong:
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    elif user == pw_not_match:
        raise HTTPException(status_code=400, detail="New password and confirmation do not match")
    return {"detail": "Password changed successfully"}
