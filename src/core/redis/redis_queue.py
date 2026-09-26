from redis import Redis
from rq import Queue


class RedisQueue:

    _instance: RedisQueue | None = None

    @classmethod
    def get_instance(cls) -> RedisQueue:
        if not cls._instance:
            cls._instance = cls()
        return cls._instance


    def __init__(self):
        self._client = Redis(
            host="localhost",
            db=1,
        )
        self._queue = Queue(
            name="task_queue",
            connection=self._client,
        )


    def get(self) -> Queue:
        return self._queue


    def close(self):
        self._client.close()