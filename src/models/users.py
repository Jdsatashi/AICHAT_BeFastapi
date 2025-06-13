from datetime import datetime
from typing import List

from sqlalchemy import String, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.models.association import table_user_roles
from src.utils.unow import now_vn


class Users(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_vn)

    messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # ... existing fields ...
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=table_user_roles,
        back_populates="users",
    )
    
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
