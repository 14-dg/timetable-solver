import logging
from datetime import UTC, datetime
from uuid import UUID

import httpx
from redis.asyncio import Redis

from core.exceptions.crud_exceptions import ObjectNotFoundException
from core.solve.solver_task_request import SolverTaskRequest
from core.solve.solver_task_status import SolverTaskStatus
from features.timetables.solver.timetable_solver import TimetableSolver
from features.timetables.timetable_service import (
    get_timetable_task_request,
    get_timetable_task_status,
    set_timetable_task_solutions,
    update_timetable_task_status,
)

logger = logging.getLogger(__name__)


async def send_webhook(task_status: SolverTaskStatus, task_request: SolverTaskRequest):
    if task_request.webhook_url:
        try:
            response: httpx.Response = httpx.post(url=task_request.webhook_url.encoded_string(), json=task_status.model_dump())
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occured on task completion webhhok.\nStatus Code: {e.response.status_code}\nError message: {e.response.text}")


async def run_timetable_task(
    redis: Redis,
    task_id: UUID,
) -> None:
    try:
        task_status: SolverTaskStatus = await get_timetable_task_status(redis, task_id)
        task_request: SolverTaskRequest = await get_timetable_task_request(redis, task_id)
    except ObjectNotFoundException:
        logger.info(f"Task {task_id} got deleted before it started.")
        return
    task_status.status = "Running"
    task_status.started_at = datetime.now(UTC)
    await update_timetable_task_status(redis, task_status)

    solver = TimetableSolver()
    timetable_solutions = solver.solve()
    task_status.completed_at = datetime.now(UTC)
    await set_timetable_task_solutions(redis, timetable_solutions)
    await update_timetable_task_status(redis, task_status)
    await send_webhook(task_status, task_request)