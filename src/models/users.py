from sqlalchemy import Column, Integer, String, Boolean, DateTime

from src.db.database import Base
from src.utils.unow import now_vn


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(120), nullable=False, unique=True, index=True)
    password = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now_vn)

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
