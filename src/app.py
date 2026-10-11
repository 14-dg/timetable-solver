from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from core.config.settings import SETTINGS
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


def start_app():
    uvicorn.run("apiexporter.app:app", host="0.0.0.0", port=SETTINGS.APP_PORT, reload=False)