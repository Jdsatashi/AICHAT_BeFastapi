import asyncio

from src.db.database import Base, engine


async def create_tables():
    from src.models.chat import ChatTopic, ChatMessage
    from src.models.users import Users
    from src.models.auth import RefreshToken
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_tables())
