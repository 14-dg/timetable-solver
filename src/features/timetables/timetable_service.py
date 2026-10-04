from uuid import UUID

from redis.asyncio import Redis

from core.config.constants import CONSTANTS
from core.exceptions.crud_exceptions import ObjectNotFoundException
from core.redis.redis_keys import TIMETABLE_KEYS, TaskDataKeys
from core.solve.solver_task_solutions import SolverTaskSolutions
from core.solve.solver_task_status import SolverTaskStatus
from core.solve.task_data import TaskData
from features.timetables.timetable_solver_task_request import TimetableSolverTaskRequest


async def create_timetable_task(redis: Redis, task_request: TimetableSolverTaskRequest) -> TaskData:
    """creates a timetable task request and status in redis"""
    task_data = TaskData(request=task_request)
    task_key = TIMETABLE_KEYS.task(task_data.task_id)
    async with redis.pipeline() as pipe:
        await pipe.hset(
            name=task_key,
            mapping={
                "task_id": str(task_data.task_id),
                "request": task_data.request.model_dump_json(),
                "status": task_data.status.model_dump_json(),
                "solutions": task_data.solutions.model_dump_json(),
            }
        )
        await pipe.expire(task_key, CONSTANTS.redis_cache_expiry.timetable.pending)
        await pipe.execute()
    return task_data


async def set_timetable_task_solutions(redis: Redis, task_id: UUID, solutions: SolverTaskSolutions) -> None:
    """sets solutions of a timetable task in redis"""
    task_key = TIMETABLE_KEYS.task(task_id)
    await redis.hset(
        name=task_key,
        key=TaskDataKeys.solutions.value,
        value=solutions.model_dump_json()
    )


async def get_timetable_task_data(redis: Redis, task_id: UUID) -> TaskData:
    """retrieves timetable tasks data (request, status, solutions)"""
    task_key = TIMETABLE_KEYS.task(task_id)
    data = await redis.hgetall(task_key)
    if not data:
        raise ObjectNotFoundException(task_id)
    
    return TaskData.model_validate(data)


async def get_timetable_task_request(redis: Redis, task_id: UUID) -> TimetableSolverTaskRequest:
    """retrieves a timetable task request"""
    task_key = TIMETABLE_KEYS.task(task_id)
    request_data = await redis.hget(
        name=task_key,
        key=TaskDataKeys.request.value,
    )
    if not request_data:
        raise ObjectNotFoundException(task_id)
    return TimetableSolverTaskRequest.model_validate_json(request_data)


async def get_timetable_task_status(redis: Redis, task_id: UUID) -> SolverTaskStatus:
    """retrieves a timetable task status"""
    task_key = TIMETABLE_KEYS.task(task_id)
    status_data = await redis.hget(
        name=task_key,
        key=TaskDataKeys.status.value,
    )
    if not status_data:
        raise ObjectNotFoundException(task_id)
    return SolverTaskStatus.model_validate_json(status_data)


async def get_timetable_task_solutions(redis: Redis, task_id: UUID) -> SolverTaskSolutions:
    """retrieves a timetable tasks solutions"""
    task_key = TIMETABLE_KEYS.task(task_id)
    solutions_data = await redis.hget(
        name=task_key,
        key=TaskDataKeys.solutions.value,
    )
    if not solutions_data:
        raise ObjectNotFoundException(task_id)
    return SolverTaskSolutions.model_validate_json(solutions_data)


async def get_all_timetable_tasks_statuses(redis: Redis) -> list[SolverTaskStatus]:
    """retrieves all timetable tasks statuses"""
    keys: list[str] = [key async for key in redis.scan_iter(TIMETABLE_KEYS.task_pattern())] # type: ignore
    if not keys:
        return []

    async with redis.pipeline() as pipe:
        for key in keys:
            await pipe.hget(name=key, key=TaskDataKeys.status.value)
        results = await pipe.execute()

    return [SolverTaskStatus.model_validate_json(data) for data in results if data]


async def update_timetable_task_status(redis: Redis, task_id: UUID, task_status: SolverTaskStatus) -> None:
    """updates the status of a timetable task in redis"""
    task_key = TIMETABLE_KEYS.task(task_id)
    async with redis.pipeline() as pipe:
        await pipe.hset(
            name=task_key,
            key=TaskDataKeys.status.value,
            value=task_status.model_dump_json(),
        )
        match task_status.status:
            case "Submitted" | "Running":
                await pipe.expire(name=task_key, time=CONSTANTS.redis_cache_expiry.timetable.pending)
            case "Completed":
                await pipe.expire(name=task_key, time=CONSTANTS.redis_cache_expiry.timetable.completed)
            case "Failed":
                await pipe.expire(name=task_key, time=CONSTANTS.redis_cache_expiry.timetable.failed)
        await pipe.execute()


async def delete_timetable_task(redis: Redis, task_id: UUID) -> None:
    """deletes requests, status and solutions of a timetable task from redis"""
    await redis.delete(TIMETABLE_KEYS.task(task_id))
