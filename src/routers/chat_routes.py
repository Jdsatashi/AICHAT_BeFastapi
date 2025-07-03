# chat_routes.py

from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from src.client_api.gpt import message_to_gpt_stream
from src.db.database import get_db
from src.handlers.jwt_token import decode_token
from src.models import ChatTopic
from src.routers.auth_routes import oauth2_scheme
from src.schema.chat_schema import TopicOutput, TopicCreate, MessageCreate, ConversationData
from src.schema.queries_params_schema import QueryParams, DataResponseModel
from src.services.chat import get_topics, create_topic, create_message, get_topic_messages, get_user_topics, \
    get_messages, get_recent_msg, create_message_socket
from src.utils.api_path import RoutePaths

chat_router = APIRouter(prefix=RoutePaths.ChatTopic.init)

""" --- Topic router handler """


@chat_router.get(RoutePaths.ChatTopic.list, response_model=DataResponseModel[TopicOutput])
async def list_topic(db: AsyncSession = Depends(get_db), queries: QueryParams = Depends()):
    return await get_topics(db, queries)


@chat_router.post(RoutePaths.ChatTopic.add, response_model=TopicOutput)
async def add_topic(topic_data: TopicCreate, db: AsyncSession = Depends(get_db)):
    new_topic = await create_topic(db, topic_data)
    return new_topic


@chat_router.get(RoutePaths.ChatTopic.list_by_user, response_model=DataResponseModel[TopicOutput])
async def list_topic_by_user(user_id: str, db: AsyncSession = Depends(get_db), queries: QueryParams = Depends()):
    return await get_user_topics(db, queries, user_id)


""" --- Message router handler """


@chat_router.get(path=RoutePaths.ChatMessage.list)
async def list_message(db: AsyncSession = Depends(get_db), queries: QueryParams = Depends()):
    return await get_messages(db, queries)


@chat_router.post(path=RoutePaths.ChatMessage.add)
async def add_message(token: Annotated[str, Depends(oauth2_scheme)], topic_id: int,
                      message_data: MessageCreate, db: AsyncSession = Depends(get_db)):
    """ Route to create a new message in a specific topic """
    conversation = ConversationData(
        topic_id=topic_id,
        token=token,
        content=message_data.content,
        user_id=None
    )
    response = await create_message(db, conversation)
    return {
        "assistant": response
    }


@chat_router.get(path=RoutePaths.ChatMessage.list_by_topic)
async def list_specific_messages(
        topic_id: int,
        db: AsyncSession = Depends(get_db),
        queries: QueryParams = Depends()
):
    """ Route get all messages of a specific topic """
    return await get_topic_messages(db, queries, topic_id)


@chat_router.get(path=RoutePaths.ChatMessage.list_by_topic_user)
async def list_specific_messages(
        topic_id: int,
        user_id: int,
        db: AsyncSession = Depends(get_db),
        queries: QueryParams = Depends()
):
    """ Route get all messages of a specific topic by user id """
    return await get_topic_messages(db, queries, topic_id, user_id)


@chat_router.websocket(path=RoutePaths.ChatMessage.socket)
async def test_socket_messages(
        websocket: WebSocket,
        topic_id: int,
        token: str,
        db: AsyncSession = Depends(get_db)
):
    """ Route WebSocket allow get response real-time """
    print("WebSocket connection attempt")

    try:
        # Get topic by ID
        topic = await db.get(ChatTopic, topic_id)
        
        # Get recent messages of topic
        messages = await get_recent_msg(db, topic)
        
        # Decode payload token
        payload = decode_token(token)
        if isinstance(payload, str) or not payload.user_id:
            return
        
        # Start WebSocket connection
        await websocket.accept()
        
        # Stream messages in a loop
        while True:
            # Receive message from WebSocket
            data = await websocket.receive_json()
            content = data.get("content")
            
            # Check content were provided
            if content:
                # Append user message to messages
                messages.append({"role": "user", "content": content})
                # Create a message in the database
                await create_message_socket(db, topic_id, payload.user_id, content, "user")
            
            # Call OpenAI API to get assistant response
            resp = message_to_gpt_stream(
                messages,
                topic.model,
                topic.temperature,
                topic.max_token,
            )
            # Init full assistant message
            assistant_message = ""
            # Loop through the response chunks
            for chunk in resp:
                assistant_response = chunk.choices[0].delta.content
                # Concat message when response is not None
                if assistant_response:
                    assistant_message += assistant_response
                # Send the response chunk to WebSocket
                await websocket.send_text(f"{assistant_response}")
            # Create assistant message in the database
            await create_message_socket(db, topic_id, payload.user_id, assistant_message, "assistant")
    except Exception as e:
        # Return None, close WebSocket connection and rollback the database transaction
        print(e)
        await db.rollback()
        await websocket.close()
        return
