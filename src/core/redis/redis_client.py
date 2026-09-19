from redis.asyncio import Redis

redis_client = Redis(
    host="localhost",
    db=0,
    decode_responses=True,
)

def get_redis_client():
    return redis_client