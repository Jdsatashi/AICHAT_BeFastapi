from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.db.database import Base
from src.utils.unow import now_vn
from .association import table_user_roles, table_role_permissions


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    group: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_vn)

    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary=table_role_permissions,
        back_populates="roles",
    )
    users: Mapped[list["Users"]] = relationship(
        "Users",
        secondary=table_user_roles,
        back_populates="roles",
    )

    def __init__(self, name: str, description: str | None = None, is_active: bool = True, group: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.description = description
        self.is_active = is_active
        self.group = group

    def __repr__(self):
        return f"<Role(name={self.name}, description={self.description}, is_active={self.is_active})>"
