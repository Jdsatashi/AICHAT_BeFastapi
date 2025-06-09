from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship

from src.db.database import Base
from src.utils.unow import now_vn


class ChatTopic(Base):
    __tablename__ = "chat_topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text(), nullable=True)
    system_prompt = Column(Text(), nullable=True)
    first_message = Column(Text(), nullable=True)

    notes = Column(Text(), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now_vn)
    updated_at = Column(DateTime, default=now_vn, onupdate=now_vn)

    # Foreign key relationships
    conversations = relationship("ChatConversation", back_populates="topic")

    def __init__(self, name: str, description: str = None, system_prompt: str = None, first_message: str = None,
                 is_active: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.first_message = first_message
        self.is_active = is_active


class ChatConversation(Base):
    __tablename__ = "chat_conversations"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)

    notes = Column(Text(), nullable=True)
    created_at = Column(DateTime, default=now_vn)

    # Foreign key relationships
    topic = relationship("ChatTopic", back_populates="conversations")
    user = relationship("Users", back_populates="conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete")

    def __init__(self, topic_id: int, user_id: int, notes: str = None, **kwargs):
        super().__init__(**kwargs)
        self.topic_id = topic_id
        self.user_id = user_id
        self.notes = notes


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, nullable=False)
    role = Column(String(50), nullable=False)  # e.g., 'user' or 'assistant'
    content = Column(Text(), nullable=False)

    created_at = Column(DateTime, default=now_vn)

    # Foreign  key relationships 
    conversation = relationship("ChatConversation", back_populates="messages")

    def __init__(self, conversation_id: int, role: str, content: str, **kwargs):
        super().__init__(**kwargs)
        self.conversation_id = conversation_id
        self.role = role
        self.content = content
