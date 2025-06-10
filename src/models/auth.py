from src.db.database import Base
from sqlalchemy import Column, Integer, Boolean, DateTime, Text

from src.utils.unow import now_vn


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer(), primary_key=True, index=True)
    refresh_token = Column(Text(), nullable=False, unique=True, index=True)
    user_id = Column(Integer(), nullable=False, index=True)
    is_active = Column(Boolean(), default=True)
    expiration = Column(DateTime(), nullable=False)
    
    created_at = Column(DateTime, default=now_vn)

    def __init__(self, refresh_token: str, user_id: int, expiration: DateTime, is_active: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.refresh_token = refresh_token
        self.user_id = user_id
        self.expiration = expiration
        self.is_active = is_active
