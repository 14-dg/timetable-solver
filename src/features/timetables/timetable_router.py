from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from rq import Queue
from rq.command import send_stop_job_command  # type: ignore

from core.redis.redis_manager import get_redis_client, get_redis_queue
from core.solve.solver_task_solutions import SolverTaskSolutions
from core.solve.solver_task_status import SolverTaskStatus
from core.solve.task_data import TaskData
from features.timetables.run_task import run_timetable_solver_task
from features.timetables.timetable_service import (
    create_timetable_task,
    delete_timetable_task,
    get_all_timetable_tasks_statuses,
    get_timetable_task_solutions,
    get_timetable_task_status,
)
from features.timetables.timetable_solver_task_request import TimetableSolverTaskRequest

RedisDep = Annotated[Redis, Depends(get_redis_client)]
QueueDep = Annotated[Queue, Depends(get_redis_queue)]

timetable_router = APIRouter(
    prefix="/timetable",
    tags=["TIMETABLE_SOLVER"]
)


@timetable_router.post(path="/", response_model=SolverTaskStatus)
async def create_timetable(
    redis_client: RedisDep,
    queue: QueueDep,
    task_request: TimetableSolverTaskRequest,
) -> SolverTaskStatus:
    task_data: TaskData = await create_timetable_task(redis_client, task_request)
    queue.enqueue( # type: ignore
        run_timetable_solver_task,
        task_data.task_id,
        job_id=str(task_data.task_id),
    )
    return task_data.status

    
@timetable_router.get(path="/", response_model=list[SolverTaskStatus])
async def get_all_status(
    redis_client: RedisDep,
) -> list[SolverTaskStatus]:
    return await get_all_timetable_tasks_statuses(redis_client)


@timetable_router.get(path="/{task_id}", response_model=SolverTaskStatus)
async def get_status(
    redis_client: RedisDep,
    task_id: UUID,
) -> SolverTaskStatus:
    return await get_timetable_task_status(redis_client, task_id)


@timetable_router.get(path="/{task_id}/solutions", response_model=SolverTaskSolutions)
async def get_solutions(
    redis_client: RedisDep,
    task_id: UUID,
) -> SolverTaskSolutions:
    return await get_timetable_task_solutions(redis_client, task_id)


@timetable_router.delete(path="/{task_id}")
async def cancel_task(
    redis_client: RedisDep,
    queue: QueueDep,
    task_id: UUID,
):
    job_id = str(task_id)
    job = queue.fetch_job(job_id)
    if job:
        # Job wartet noch in der Queue -> Einfach entfernen
        if job.is_queued:
            job.cancel()
        # Job wird gerade vom Worker berechnet -> Signal zum Abbruch senden
        elif job.is_started:
            send_stop_job_command(queue.connection, job_id)
    
    await delete_timetable_task(redis_client, task_id)

    return {"detail": f"Task {task_id} was cancelled successfully."}