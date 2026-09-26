from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.exceptions.exception_handler import (
    add_app_exception_handlers,
)
from core.redis.redis_manager import close_redis, init_redis
from features.timetables.timetable_router import timetable_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_redis()

    yield

    await close_redis()


app = FastAPI(
    title="Roomfinder Solver Service",
    version="0.0.1",
    lifespan=lifespan
)


app.include_router(timetable_router)

add_app_exception_handlers(app)