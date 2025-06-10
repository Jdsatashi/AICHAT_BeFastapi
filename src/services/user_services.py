from typing import Type

from sqlalchemy.orm import Session

from src.schema.user_schema import UserCreate, UserSelfUpdate, ChangePassword
from src.handlers.pw_hash import hash_pass, verify_password
from src.models.users import Users
from src.utils.constant import pw_wrong, pw_not_match


def get_all_users(db: Session):
    return db.query(Users).all()


def create_user(db: Session, user_data: UserCreate) -> Users:
    password = hash_pass(user_data.password)

    db_user = Users(
        username=user_data.username,
        email=str(user_data.email),
        password=password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_id(db: Session, user_id: int) -> Type[Users] | None:
    return db.query(Users).filter(Users.id == user_id).first()


def update_user_self(db: Session, user_id: int, user_data: UserSelfUpdate) -> Type[Users] | None:
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        return None

    if user_data.username:
        user.username = user_data.username
    if user_data.email:
        user.email = str(user_data.email)

    db.commit()
    db.refresh(user)
    return user


def destroy_user(db: Session, user_id: int) -> bool | None:
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        return None
    try:
        db.delete(user)
        db.commit()

        return True
    except Exception as e:
        db.rollback()
        print(f"Error deleting user: {e}")
        return False


def change_password(db: Session, user_id: int, user_data: ChangePassword) -> str | None | bool:
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        return None
    # check_pw = verify_password(user_data.old_password, user.password)
    if not user.check_pw(pw=user_data.old_password):
        return pw_wrong

    if user_data.new_password != user_data.confirm_new_password:
        return pw_not_match

    user.password = hash_pass(user_data.new_password)
    db.commit()
    db.refresh(user)
    return True
