import redis.asyncio as aioredis

from src.conf.settings import REDIS_HOST, REDIS_PORT, REDIS_DB

redis_client = aioredis.from_url(
    f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
    encoding="utf-8",
    decode_responses=True,
)

# Key for storing redis data
store_token = "access_token"