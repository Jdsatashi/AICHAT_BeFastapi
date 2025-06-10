from pydantic import BaseModel


class CreateChatTopic(BaseModel):
    name: str
    description: str | None = None
    system_prompt: str
    first_message: str | None = None
    notes: str | None = None