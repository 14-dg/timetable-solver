from redis.asyncio import Redis


class RedisClient:

    _instance: RedisClient | None = None

    @classmethod
    def get_instance(cls) -> RedisClient:
        if not cls._instance:
            cls._instance = cls()
        return cls._instance


    def __init__(self) -> None:
        self._client = Redis(
            host="localhost",
            db=0,
            decode_responses=True,
        )


    def get(self) -> Redis:
        return self._client


    async def close(self) -> None:
        if self._client:
            await self._client.aclose()