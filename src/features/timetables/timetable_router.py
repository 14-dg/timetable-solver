from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from rq import Queue

from core.redis.redis_manager import get_redis_client, get_redis_queue
from core.tasks.solver_task_request import SolverTaskRequest
from core.tasks.solver_task_solutions import SolverTaskSolutions
from core.tasks.solver_task_status import SolverTaskStatus

RedisDep = Annotated[Redis, Depends(get_redis_client)]
QueueDep = Annotated[Queue, Depends(get_redis_queue)]

timetable_router = APIRouter(
    prefix="/timetable",
    tags=["TIMETABLE_SOLVER"]
)


@timetable_router.post(path="/")
async def create_timetable(
    redis_client: RedisDep,
    queue: QueueDep,
    task_request: SolverTaskRequest,
) -> SolverTaskStatus:
    task_status = await create_solver_task(redis_client, task_request)
    queue.enqueue(run_solver_task, redis_client, task_status.task_id) # type: ignore
    return task_status

    
@timetable_router.get(path="/")
async def get_all_status(
    redis_client: RedisDep,
) -> list[SolverTaskStatus]:
    return await get_all_tasks_status(redis_client)


@timetable_router.get(path="/{task_id}")
async def get_status(
    redis_client: RedisDep,
    task_id: UUID,
) -> SolverTaskStatus:
    return await get_timetable_task_status(redis_client, task_id)


@timetable_router.get(path="/{task_id}/solutions")
async def get_solutions(
    redis_client: RedisDep,
    task_id: UUID,
) -> SolverTaskSolutions:
    return await get_timetable_task_solutions(redis_client, task_id)


@timetable_router.delete(path="/{task_id}")
async def cancel_task(
    redis_client: RedisDep,
    task_id: UUID,
):
    return await delete_timetable_task(redis_client, task_id)