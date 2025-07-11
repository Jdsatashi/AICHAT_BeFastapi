from typing import Optional

from pydantic import BaseModel


class TopicCreate(BaseModel):
    name: str
    description: Optional[str]

    model: Optional[str] = None
    system_prompt: str
    temperature: float
    max_token: int
    max_msg_retrieve: Optional[int]
    
    notes: Optional[str]
    origin_user: int

    class Config:
        orm_mode = True


class TopicUpdate(BaseModel):
    name: str
    description: Optional[str]
    notes: Optional[str]
    temperature: float
    max_token: int

    class Config:
        orm_mode = True


class TopicOutput(BaseModel):
    id: int
    name: str
    description: Optional[str]
    model: str
    system_prompt: str
    temperature: float
    max_token: int
    max_msg_retrieve: int
    notes: Optional[str]
    origin_user: Optional[int]

    class Config:
        orm_mode = True


# """ --- Message Schema --- """
class MessageCreate(BaseModel):
    content: str


class ConversationData(BaseModel):
    content: str
    topic_id: int
    user_id: Optional[int]
    token: Optional[str]
