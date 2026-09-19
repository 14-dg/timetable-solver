from core.redis.redis_client import get_redis_client


async def get_pipeline():
    client = get_redis_client()
    async with client.pipeline(transaction=True) as pipe:
        yield pipe
        await pipe.execute()