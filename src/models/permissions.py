from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.models.association import table_role_permissions
from src.utils.unow import now_vn


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), index=True, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    object_pk: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    depend_on: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, default=None)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_vn)

    def __init__(self, name: str, description: str, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.description = description

    def __repr__(self):
        return f"<Perms(name={self.name}, description={self.description})>"

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=table_role_permissions,
        back_populates="permissions",
    )
