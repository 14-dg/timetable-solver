import logging
from datetime import UTC, datetime
from uuid import UUID

import httpx
from redis.asyncio import Redis

from core.exceptions.crud_exceptions import ObjectNotFoundException
from core.solve.base_solver import BaseSolver
from core.tasks.solver_task_request import SolverTaskRequest
from core.tasks.solver_task_solutions import SolverTaskSolutions
from core.tasks.solver_task_status import SolverTaskStatus
from core.tasks.task_service import (
    get_solver_task_request,
    get_solver_task_status,
    set_solver_task_solutions,
    update_solver_task_status,
)

logger = logging.getLogger(__name__)


async def send_webhook(url: str, task_status: SolverTaskStatus):
    async with httpx.AsyncClient() as client:
        try:
            response: httpx.Response = await client.post(url=url, json=task_status.model_dump())
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occured on task completion webhhok.\nStatus Code: {e.response.status_code}\nError message: {e.response.text}")


async def run_solver_task(
    redis: Redis,
    task_id: UUID,
    solver: BaseSolver,
) -> None:
    try:
        task_status: SolverTaskStatus = await get_solver_task_status(redis, task_id)
        task_request: SolverTaskRequest = await get_solver_task_request(redis, task_id)
    except ObjectNotFoundException:
        logger.info(f"Task {task_id} got deleted before it started.")
        return
    task_status.status = "Running"
    task_status.started_at = datetime.now(UTC)
    await update_solver_task_status(redis, task_status)

    solutions: SolverTaskSolutions = solver.solve()
    task_status.completed_at = datetime.now(UTC)
    await set_solver_task_solutions(redis, solutions)
    await update_solver_task_status(redis, task_status)
    if task_request.webhook_url:
        # TODO den request nicht blockierend machen
        await send_webhook(task_request.webhook_url.encoded_string(), task_status)