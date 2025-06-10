from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base
from src.utils.unow import now_vn


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_vn)

    def __init__(self, username: str, email: str, password: str, is_active: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.email = email
        self.password = password
        self.is_active = is_active

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email}, is_active={self.is_active})>"

    def check_pw(self, pw: str) -> bool:
        """Check if the provided password matches the stored password."""
        from src.conf.settings import PWD_CONTEXT
        return PWD_CONTEXT.verify(pw, self.password)
