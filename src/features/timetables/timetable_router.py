from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from rq import Queue

from core.redis.redis_manager import get_redis_client, get_redis_queue
from features.timetables.schemas.timetable_task_request import TimetableTaskRequest
from features.timetables.schemas.timetable_task_solutions import TimetableTaskSolutions
from features.timetables.schemas.timetable_task_status import TimetableTaskStatus
from features.timetables.timetable_service import (
    create_timetable_task,
    delete_timetable_task,
    get_all_timetable_tasks_status,
    get_timetable_task_solutions,
    get_timetable_task_status,
)

RedisDep = Annotated[Redis, Depends(get_redis_client)]
QueueDep = Annotated[Queue, Depends(get_redis_queue)]

timetable_router = APIRouter(
    prefix="/timetable",
    tags=["TIMETABLE_SOLVER"]
)


@timetable_router.post(path="/")
async def create_timetable(
    client: RedisDep,
    queue: QueueDep,
    task_request: TimetableTaskRequest,
) -> TimetableTaskStatus:
    return await create_timetable_task(client, queue, task_request)


@timetable_router.get(path="/")
async def get_all_status(
    client: RedisDep,
) -> list[TimetableTaskStatus]:
    return await get_all_timetable_tasks_status(client)


@timetable_router.get(path="/{task_id}")
async def get_status(
    client: RedisDep,
    task_id: UUID,
) -> TimetableTaskStatus:
    return await get_timetable_task_status(client, task_id)


@timetable_router.get(path="/{task_id}/solutions")
async def get_solutions(
    client: RedisDep,
    task_id: UUID,
) -> TimetableTaskSolutions:
    return await get_timetable_task_solutions(client, task_id)


@timetable_router.delete(path="/{task_id}")
async def cancel_task(
    client: RedisDep,
    task_id: UUID,
):
    return await delete_timetable_task(client, task_id)