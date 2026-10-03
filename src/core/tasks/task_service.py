from uuid import UUID

from redis.asyncio import Redis

from core.config.constants import CONSTANTS
from core.exceptions.crud_exceptions import ObjectNotFoundException
from core.redis.redis_keys import RedisKeys
from core.tasks.solver_task_request import SolverTaskRequest
from core.tasks.solver_task_solutions import SolverTaskSolutions
from core.tasks.solver_task_status import SolverTaskStatus


async def create_solver_task(redis: Redis, task_request: SolverTaskRequest) -> SolverTaskStatus:
    """creates a solver task request and status in redis"""
    task_status = SolverTaskStatus()

    async with redis.pipeline() as pipeline:

        pipeline.set(
            name=RedisKeys.status.one(task_status.task_id),
            value=task_status.model_dump_json(),
            ex=CONSTANTS.redis_cache_expiry.timetable,
        )

        pipeline.set(
            name=RedisKeys.request.one(task_status.task_id),
            value=task_request.model_dump_json(),
            ex=CONSTANTS.redis_cache_expiry.timetable,
        )

        await pipeline.execute()

    return task_status


async def set_solver_task_solutions(redis: Redis, solutions: SolverTaskSolutions) -> None:
    """sets a solution of a solver task in redis"""
    await redis.set(
        name=RedisKeys.solutions.one(solutions.task_id),
        value=solutions.model_dump_json(),
        ex=CONSTANTS.redis_cache_expiry.timetable,
    )


async def get_solver_task_request(redis: Redis, task_id: UUID) -> SolverTaskRequest:
    """retrieves a solver task request"""
    data = await redis.get(RedisKeys.request.one(task_id))
    if not data:
        raise ObjectNotFoundException(task_id)
    return SolverTaskRequest.model_validate_json(data)


async def get_solver_task_status(redis: Redis, task_id: UUID) -> SolverTaskStatus:
    """retrieves a solver task status"""
    data = await redis.get(RedisKeys.status.one(task_id))
    if not data:
        raise ObjectNotFoundException(task_id)
    return SolverTaskStatus.model_validate_json(data)


async def get_solver_task_solutions(redis: Redis, task_id: UUID) -> SolverTaskSolutions:
    """retrieves a solver task solution"""
    data = await redis.get(RedisKeys.solutions.one(task_id))
    if not data:
        raise ObjectNotFoundException(task_id)
    return SolverTaskSolutions.model_validate_json(data)


async def get_all_solver_tasks_statuses(redis: Redis) -> list[SolverTaskStatus]:
    """retrieves all solver tasks statuses"""
    keys: list[str] = [key async for key in redis.scan_iter(RedisKeys.status.all())] # type: ignore
    if not keys:
        return []
    results = await redis.mget(keys)
    return [SolverTaskStatus.model_validate_json(data) for data in results if data]


async def update_solver_task_status(redis: Redis, task_status: SolverTaskStatus) -> None:
    """updates the status if a solver task in redis"""
    await redis.set(
        name=RedisKeys.status.one(task_status.task_id),
        value=task_status.model_dump_json(),
        ex=CONSTANTS.redis_cache_expiry.timetable,
    )


async def delete_solver_task(redis: Redis, task_id: UUID) -> None:
    """deletes requests, status and solutions of a solver task from redis"""
    async with redis.pipeline() as pipeline:
        pipeline.delete(RedisKeys.request.one(task_id))
        pipeline.delete(RedisKeys.status.one(task_id))
        pipeline.delete(RedisKeys.solutions.one(task_id))
        await pipeline.execute()