# src/models/__init__.py

from src.db.database import Base

# import theo thứ tự để tránh missing metadata
from src.models.users import Users
from src.models.permissions import Permission
from src.models.roles import Role
from src.models.association import table_role_permissions, table_user_roles
from src.models.chat import ChatTopic, ChatConversation, ChatMessage


MODEL_REGISTRY = {
    "Users": Users,
    "Permission": Permission,
    "Role": Role,
    "ChatTopic": ChatTopic,
    "ChatMessage": ChatMessage,
    "ChatConversation": ChatConversation,
}

def get_model(name: str):
    return MODEL_REGISTRY[name]
