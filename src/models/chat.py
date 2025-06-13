from datetime import datetime
from typing import Optional, List

from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.utils.gpt_model import gpt_dtemp, gpt_dmodel, gpt_max_token
from src.utils.unow import now_vn


# --- ChatTopic ---
class ChatTopic(Base):
    __tablename__ = "chat_topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model: Mapped[str] = mapped_column(String(50), nullable=False, default=gpt_dmodel)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    temperature: Mapped[Optional[float]] = mapped_column(Float, default=gpt_dtemp)
    max_token: Mapped[Optional[int]] = mapped_column(Integer, default=gpt_max_token)
    first_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    origin_user: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_vn)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now_vn, onupdate=now_vn)

    messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="topic",
        cascade="all, delete-orphan"
    )


# --- ChatMessage ---
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_vn)

    topic_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("chat_topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    topic: Mapped[ChatTopic] = relationship(
        "ChatTopic",
        back_populates="messages"
    )
    user: Mapped["Users"] = relationship(
        "Users",
        back_populates="messages"
    )
