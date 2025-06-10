from datetime import datetime

from sqlalchemy import Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from src.db.database import Base
from src.utils.unow import now_vn


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    refresh_token: Mapped[str] = mapped_column(Text(), nullable=False, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    expiration: Mapped[datetime] = mapped_column(DateTime(), nullable=False)

    created_at = mapped_column(DateTime, default=now_vn)

    def __init__(self, refresh_token: str, user_id: int, expiration: datetime, is_active: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.refresh_token = refresh_token
        self.user_id = user_id
        self.is_active = is_active
        self.expiration = expiration
