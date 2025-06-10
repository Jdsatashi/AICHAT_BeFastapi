import redis

from src.conf.settings import REDIS_HOST, REDIS_PORT, REDIS_DB

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

# Key for storing redis data
store_token = "access_token"