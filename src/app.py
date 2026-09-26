from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.exceptions.exception_handler import (
    add_app_exception_handlers,
)
from core.redis.redis_client import RedisClient
from core.redis.redis_queue import RedisQueue
from features.timetables.timetable_router import timetable_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    redis_client = RedisClient()
    redis_queue = RedisQueue()

    yield

    await redis_client.close()
    redis_queue.close()


app = FastAPI(
    title="Roomfinder Solver Service",
    version="0.0.1",
    lifespan=lifespan
)


app.include_router(timetable_router)

add_app_exception_handlers(app)