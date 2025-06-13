from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.client_api.gpt import message_to_gpt
from src.handlers.jwt_token import decode_token
from src.models import ChatTopic, ChatMessage
from src.schema.auth_schema import TokenPayload
from src.schema.chat_schema import TopicCreate, TopicUpdate, ConversationData
from src.schema.queries_params_schema import QueryParams
from src.services.generic_services import get_all
from src.utils.err_msg import err_msg


async def get_topics(db: AsyncSession, queries: QueryParams):
    """
        Function to fetching chat topics and searching by queries from the database.
    """
    return await get_all(db, ChatTopic, queries)


async def create_topic(db: AsyncSession, topic_data: TopicCreate):
    """
        Function to creating a new chat topic in the database.
    """
    topic_input = topic_data.model_dump(exclude_unset=True)
    new_topic = ChatTopic(**topic_input)
    db.add(new_topic)
    await db.commit()
    await db.refresh(new_topic)
    return new_topic


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
    return await get_all(db, queries)


async def create_message(db: AsyncSession, conversation_data: ConversationData):
    """ Function to conversation with AI """
    # Get user id from token
    payload: TokenPayload = decode_token(conversation_data.token)

    # Get topic
    topic: ChatTopic = await db.get(ChatTopic, conversation_data.topic_id)
    if topic is None:
        return "topic " + err_msg.not_found
    msg = ChatMessage(
        user_id=payload.user_id,
        topic_id=topic.id,
        role="user",
        content=conversation_data.content
    )
    db.add(msg)
    messages = []
    if topic.system_prompt:
        messages.append({"role": "system", "content": topic.system_prompt})

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.topic_id == topic.id)
        .order_by(desc(ChatMessage.created_at))
        .limit(10)
    )
    last_msgs = result.scalars().all()
    # Đảo lại cho thành thứ tự từ cũ → mới
    last_msgs.reverse()

    # messages.append({"role": last_msgs, "content": conversation_data.content})
    for m in last_msgs:
        messages.append({"role": m.role, "content": m.content})

    print(messages)
    assistant_content = message_to_gpt(
        messages=messages,
        model=topic.model,
        temperature=topic.temperature,
        max_tokens=topic.max_token
    )

    assistant_msg = ChatMessage(
        user_id=payload.user_id,
        topic_id=topic.id,
        role="assistant",
        content=assistant_content
    )
    db.add(assistant_msg)

    await db.commit()
    await db.refresh(assistant_msg)
    await db.refresh(msg)

    return assistant_content
