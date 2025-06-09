from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.cores.user_schema import UserCreate, UserOut, UserSelfUpdate, ChangePassword
from src.db.database import get_db
from src.services.user_services import get_all_users, get_user_by_id, create_user, update_user_self, destroy_user, \
    change_password
from src.utils.constant import pw_wrong, pw_not_match

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get("/", response_model=List[UserOut])
def read_users(db: Session = Depends(get_db)):
    return get_all_users(db)


@user_router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_route(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)


@user_router.get("/{user_id}", response_model=UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.put("/{user_id}", response_model=UserOut)
def self_update_user(user_id: int, user_data: UserSelfUpdate, db: Session = Depends(get_db)):
    user = update_user_self(db, user_id, user_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    result = destroy_user(db, user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    elif not result:
        raise HTTPException(status_code=500, detail="Error deleting user")
    return {"detail": "User deleted successfully"}


@user_router.put("/{user_id}/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password_user(user_id: int, change_data: ChangePassword, db: Session = Depends(get_db)):
    user = change_password(db, user_id, change_data)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    elif user == pw_wrong:
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    elif user == pw_not_match:
        raise HTTPException(status_code=400, detail="New password and confirmation do not match")
    return {"detail": "Password changed successfully"}
