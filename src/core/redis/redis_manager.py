from redis import Redis as SyncRedis
from redis.asyncio import Redis as AsyncRedis
from rq import Queue

from core.config.settings import SETTINGS

_async_client: AsyncRedis | None = None
_sync_client: SyncRedis | None = None
_queue: Queue | None = None

async def init_redis():
    
    global _async_client, _sync_client, _queue

    _async_client = AsyncRedis(
        host=SETTINGS.REDIS_CLIENT_URL,
        decode_responses=True,
        db=0,
    )
    
    _sync_client = SyncRedis(
        SETTINGS.REDIS_QUEUE_URL,
        db=1,
    )
    _queue = Queue(name="task_queue", connection=_sync_client)

async def close_redis():
    if _async_client:
        await _async_client.aclose()
    if _sync_client:
        _sync_client.close()


def get_redis_client() -> AsyncRedis:
    if _async_client is None:
        raise RuntimeError("Async Redis is not initialized")
    return _async_client


def get_redis_queue() -> Queue:
    if _queue is None:
        raise RuntimeError("RQ Queue is not initialized")
    return _queue