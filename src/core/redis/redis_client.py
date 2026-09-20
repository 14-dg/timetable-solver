from redis.asyncio import Redis

redis_client: Redis | None = None


def create_redis_client():
    global redis_client
    redis_client = Redis(
        host="localhost",
        db=0,
        decode_responses=True,
    )

def get_redis():
    return redis_client