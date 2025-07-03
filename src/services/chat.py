from typing import Literal

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.responses import JSONResponse

from src.client_api.gpt import message_to_gpt
from src.conf.settings import DEBUG
from src.handlers.jwt_token import decode_token
from src.handlers.perm import generate_perm
from src.models import ChatTopic, ChatMessage, Permission, Role, Users
from src.schema.auth_schema import TokenPayload
from src.schema.chat_schema import TopicCreate, TopicUpdate, ConversationData
from src.schema.queries_params_schema import QueryParams
from src.services.generic_services import get_all
from src.services.perm_services import create_main_perms
from src.utils.err_msg import err_msg
from src.utils.perm_actions import actions


async def get_topics(db: AsyncSession, queries: QueryParams):
    """
        Function to fetching chat topics and searching by queries from the database.
    """
    return await get_all(db, ChatTopic, queries)


async def get_user_topics(db: AsyncSession, queries: QueryParams, user_id: str):
    """
        Function to fetching chat topics of specific user and searching by queries from the database.
    """
    return await get_all(db, ChatTopic, queries,
                         external_query=select(ChatTopic).filter(ChatTopic.origin_user == user_id))


async def create_topic(db: AsyncSession, topic_data: TopicCreate):
    """
        Function to creating a new chat topic in the database.
    """
    try:
        topic_input = topic_data.model_dump(exclude_unset=True)
        new_topic = ChatTopic(**topic_input)
        db.add(new_topic)
        await db.flush()

        topic_perms: list[Permission] = await create_main_perms(db, ChatTopic.__name__, new_topic.id)

        # Create role for topic
        new_role = Role(name=f"Topic {new_topic.id}",
                        description=f"Role access topic {new_topic.id}",
                        is_active=True,
                        group=False)

        # Get role self user
        role_user = f'{Users.__name__}_{new_topic.origin_user}'
        result = await db.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(
                Role.name == role_user,
            )
        )
        user_role = result.scalar_one_or_none()

        add_perms = [topic_perm for topic_perm in topic_perms if
                     topic_perm.name.split("_")[0] in [actions.read, actions.add]]
        # Create permissions message to topic
        for perm in topic_perms:
            action_name = perm.name.split("_")[0]
            if action_name in [actions.add, actions.edit]:
                msg_perm: Permission = await generate_perm(
                    ChatMessage.__name__,
                    action=action_name,
                    obj_id=new_topic.id,
                    depend_on=perm.name,
                    db=db
                )
                db.add(msg_perm)
                add_perms.append(msg_perm)

        await db.flush()
        user_role.permissions.extend(add_perms)

        await db.commit()
        return new_topic
    except Exception as e:
        await db.rollback()
        if DEBUG:
            raise e
        print(e)
        return JSONResponse(status_code=400, content={"error": str(e)})


async def get_topic(db: AsyncSession, topic_id: int):
    """ Function to get specific topic by id """
    return await db.get(ChatTopic, topic_id)


async def update_topic(db: AsyncSession, topic_data: TopicUpdate, topic_id: int):
    """ Function update topic except system_prompt and first meet greeting """
    # Get topic by id
    topic = db.get(ChatTopic, topic_id)
    # Return error if not found
    if topic is None:
        return err_msg.not_found

    # Update data by fields
    topic.name = topic_data.name
    if topic_data.description:
        topic.description = topic_data.description
    if topic_data.notes:
        topic.notes = topic_data.notes

    # Commit change to db
    await db.commit()
    await db.refresh(topic)
    return topic


""" --- Conversation Service --- """


async def get_messages(db: AsyncSession, queries: QueryParams):
    """
        Function to fetching chat conversations and searching by queries from the database.
    """
    return await get_all(db, ChatMessage, queries)


async def get_topic_messages(db: AsyncSession, queries: QueryParams, topic_id: int, user_id: int = 0):
    stmt = select(ChatMessage)
    query = (stmt.filter(ChatMessage.topic_id == topic_id) if user_id == 0
             else stmt.filter(ChatMessage.topic_id == topic_id, ChatMessage.user_id == user_id))
    result = await get_all(db, ChatMessage, queries, external_query=query)
    return result


async def create_message(db: AsyncSession, conversation_data: ConversationData):
    """ Function to conversation with AI """
    # Get user id from token
    payload: TokenPayload = decode_token(conversation_data.token)

    # Get topic
    topic: ChatTopic | None = await db.get(ChatTopic, conversation_data.topic_id)
    if topic is None:
        return "topic " + err_msg.not_found

    # Create message by user
    msg = await create_message_socket(db, topic.id, payload.user_id, conversation_data.content, "user")
    await db.refresh(msg)

    messages = await get_recent_msg(db, topic)

    assistant_content = message_to_gpt(
        messages=messages,
        model=topic.model,
        temperature=topic.temperature,
        max_tokens=topic.max_token
    )

    await create_message_socket(db, topic.id, payload.user_id, assistant_content, "assistant")

    return assistant_content


async def get_recent_msg(db: AsyncSession, topic: ChatTopic):
    """ Function get recent message of topic """
    messages = []
    if topic.system_prompt:
        messages.append({"role": "system", "content": topic.system_prompt})
    # Query recent messages with limit
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.topic_id == topic.id)
        .order_by(desc(ChatMessage.created_at))
        .limit(topic.max_msg_retrieve * 2)
    )
    last_msgs = result.scalars().all()
    # Reverse response of database
    last_msgs.reverse()
    for m in last_msgs:
        messages.append({"role": m.role, "content": m.content})
    return messages


async def create_message_socket(db: AsyncSession, topic_id: int, user_id: int, content: str,
                                role: Literal["user", "assistant"]):
    """ Function to create message by socket """
    msg = ChatMessage(
        user_id=user_id,
        topic_id=topic_id,
        role=role,
        content=content
    )
    db.add(msg)
    await db.commit()
    return msg
