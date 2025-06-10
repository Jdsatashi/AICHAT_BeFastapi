from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.utils.unow import now_vn

# --- ChatTopic ---
class ChatTopic(Base):
    __tablename__ = "chat_topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="")
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    first_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_vn)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now_vn, onupdate=now_vn)

    conversations: Mapped[list["ChatConversation"]] = relationship(
        "ChatConversation",
        back_populates="topic",
        cascade="all, delete-orphan"
    )


# --- ChatConversation ---
class ChatConversation(Base):
    __tablename__ = "chat_conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("chat_topics.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_vn)

    topic: Mapped[ChatTopic] = relationship("ChatTopic", back_populates="conversations")
    user: Mapped["Users"] = relationship("Users", back_populates="conversations")
    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )


# --- ChatMessage ---
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_vn)

    conversation: Mapped[ChatConversation] = relationship(
        "ChatConversation",
        back_populates="messages"
    )