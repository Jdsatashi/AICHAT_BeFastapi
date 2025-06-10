from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.conf import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    db: AsyncSession = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()