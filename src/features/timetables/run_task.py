import asyncio
import logging
from datetime import UTC, datetime
from uuid import UUID

from redis.asyncio import Redis

from core.exceptions.crud_exceptions import ObjectNotFoundException
from core.redis.redis_manager import create_async_redis_client
from core.solve.solver_exceptions import SolverTaskException
from core.solve.solver_task_solutions import SolverTaskSolutions
from core.solve.solver_task_status import SolverTaskStatus
from features.notifications.notification import send_webhook
from features.timetables.output_models.timetable_solution import TimetableSolution
from features.timetables.solver.timetable_solver import TimetableSolver
from features.timetables.timetable_service import (
    get_timetable_task_request,
    get_timetable_task_status,
    set_timetable_task_solutions,
    update_timetable_task_status,
)
from features.timetables.timetable_task_request import TimetableTaskRequest

logger = logging.getLogger(__name__)


def run_timetable_solver_task(task_id: UUID) -> None:
    """
    asyncio.run() ist zwar blockeirend,
    aber diese funktion wird nur von einem RQ worker in einem separatem prozess ausgeführt
    und blockiert die api nicht
    """
    asyncio.run(_run_timetable_solver_task(task_id))


async def _run_timetable_solver_task(task_id: UUID) -> None:
    # der worker ist ein eigener prozess ohne fastapi lifespan, deshalb eigener client.
    # pro task neu, weil asyncio.run() jedes mal einen neuen event loop startet
    redis: Redis = create_async_redis_client()
    try:
        await _solve_and_store(redis, task_id)
    finally:
        await redis.aclose()


async def _solve_and_store(redis: Redis, task_id: UUID) -> None:
    try:
        task_status: SolverTaskStatus = await get_timetable_task_status(redis, task_id)
        task_request: TimetableTaskRequest = await get_timetable_task_request(redis, task_id)
    except ObjectNotFoundException:
        logger.info(f"Task {task_id} got deleted before it started.")
        return
    task_status.status = "Running"
    task_status.started_at = datetime.now(UTC)
    await update_timetable_task_status(redis, task_id, task_status)

    try:
        solver = TimetableSolver(problem_data=task_request.problem_data)
        solutions: SolverTaskSolutions[TimetableSolution] = solver.solve()
        await set_timetable_task_solutions(redis, task_id, solutions)
        task_status.status = "Completed"
        
    except Exception as e:
        task_status.status = "Failed"
        match e:
            case SolverTaskException(): task_status.error = e.message
            case Exception(): task_status.error = "Unknown Exception"
        logger.exception(f"Solver Error in Task {task_id}")

    task_status.completed_at = datetime.now(UTC)

    await update_timetable_task_status(redis, task_id, task_status)

    if task_request.webhook_url:
        await send_webhook(task_request.webhook_url.encoded_string(), task_status)