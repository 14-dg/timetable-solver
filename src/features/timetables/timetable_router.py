from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from core.redis.redis_client import get_redis
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

Redis_Dep = Annotated[Redis, Depends(get_redis)]

timetable_router = APIRouter(
    prefix="/timetable",
    tags=["TIMETABLE_SOLVER"]
)


@timetable_router.post(path="/")
async def create_timetable(
    client: Redis_Dep,
    task_request: TimetableTaskRequest,
) -> TimetableTaskStatus:
    return await create_timetable_task(client, task_request)


@timetable_router.get(path="/")
async def get_all_status(
    client: Redis_Dep,
) -> list[TimetableTaskStatus]:
    return await get_all_timetable_tasks_status(client,)


@timetable_router.get(path="/{task_id}")
async def get_status(
    client: Redis_Dep,
    task_id: UUID,
) -> TimetableTaskStatus:
    return await get_timetable_task_status(client, task_id)


@timetable_router.get(path="/{task_id}/solutions")
async def get_solutions(
    client: Redis_Dep,
    task_id: UUID,
) -> TimetableTaskSolutions:
    return await get_timetable_task_solutions(client, task_id)


@timetable_router.delete(path="/{task_id}")
async def cancel_task(
    client: Redis_Dep,
    task_id: UUID,
):
    return await delete_timetable_task(client, task_id)