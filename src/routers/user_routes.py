from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.schema.queries_params_schema import QueryParams, DataResponseModel
from src.schema.user_schema import UserCreate, UserOutput, UserSelfUpdate, ChangePassword
from src.services.user_services import get_users, create_user, get_user, update_user, delete_user, change_password
from src.utils.err_msg import err_msg

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
    # Handle error 404
    if user == err_msg.not_found:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await delete_user(db, user_id)
    # Handle error 404
    if result == err_msg.not_found:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}


@user_router.put("/{user_id}/change-password", status_code=status.HTTP_200_OK)
async def change_password_user(user_id: int, change_data: ChangePassword, db: AsyncSession = Depends(get_db)):
    user = await change_password(db, user_id, change_data)
    # Handle error 404
    if user == err_msg.not_found:
        raise HTTPException(status_code=404, detail="User not found")
    # Handle validation error
    elif user == err_msg.pw_wrong:
        raise HTTPException(status_code=400, detail=f"Old {err_msg.pw_wrong}")
    elif user == err_msg.pw_not_match:
        raise HTTPException(status_code=400, detail=f"New password and {err_msg.pw_not_match}")
    return {"detail": "Password changed successfully"}
