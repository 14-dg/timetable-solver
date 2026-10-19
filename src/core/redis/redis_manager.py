from redis import Redis as SyncRedis
from redis.asyncio import Redis as AsyncRedis
from rq import Queue

from core.config.settings import SETTINGS

# muss mit dem queue namen im worker command (docker-compose.yaml) übereinstimmen
TASK_QUEUE_NAME = "task_queue"

_async_client: AsyncRedis | None = None
_sync_client: SyncRedis | None = None
_queue: Queue | None = None


def create_async_redis_client() -> AsyncRedis:
    """
    erstellt einen neuen async redis client.
    die db nummer ist teil der url (redis://host:port/db)
    """
    return AsyncRedis.from_url(SETTINGS.REDIS_URL, decode_responses=True)


async def init_redis():

    global _async_client, _sync_client, _queue

    _async_client = create_async_redis_client()

    # rq braucht bytes, deshalb hier kein decode_responses
    _sync_client = SyncRedis.from_url(SETTINGS.REDIS_QUEUE_URL)
    _queue = Queue(name=TASK_QUEUE_NAME, connection=_sync_client)

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
