from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.routers.auth_routes import oauth2_scheme
from src.schema.chat_schema import TopicOutput, TopicCreate, MessageCreate, ConversationData
from src.schema.queries_params_schema import QueryParams, DataResponseModel
from src.services.chat import get_topics, create_topic, create_message

chat_router = APIRouter(prefix="/chat-gpt")



""" --- Topic router handler """
@chat_router.get("/topic", response_model=DataResponseModel[TopicOutput])
async def list_topic(db: AsyncSession = Depends(get_db), queries: QueryParams = Depends()):
    return await get_topics(db, queries)


@chat_router.post("/topic", response_model=TopicOutput)
async def add_topic(topic_data: TopicCreate, db: AsyncSession = Depends(get_db)):
    new_topic = await create_topic(db, topic_data)
    return new_topic


""" --- Message router handler """
@chat_router.get(path="/messages")
async def list_message(db: AsyncSession = Depends(get_db), queries: QueryParams = Depends()):
    return

@chat_router.post(path="/topic/{topic_id}/messages")
async def add_message(token: Annotated[str, Depends(oauth2_scheme)], topic_id: int, 
                      message_data: MessageCreate, db: AsyncSession = Depends(get_db)):
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