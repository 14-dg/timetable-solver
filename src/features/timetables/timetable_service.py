from uuid import UUID

from pydantic import TypeAdapter
from redis.asyncio import Redis

from core.config.constants import CONSTANTS
from core.exceptions.crud_exceptions import ObjectNotFoundException
from features.timetables.schemas.timetable_redis_keys import TimetableRedisKeys
from features.timetables.schemas.timetable_task_request import TimetableTaskRequest
from features.timetables.schemas.timetable_task_solutions import TimetableTaskSolutions
from features.timetables.schemas.timetable_task_status import TimetableTaskStatus

adapter = TypeAdapter(list[TimetableTaskStatus])


async def create_timetable_task(redis: Redis, task_request: TimetableTaskRequest) -> TimetableTaskStatus:
    """creates a timetable request and status in redis"""
    task_status = TimetableTaskStatus()

    async with redis.pipeline() as pipeline:

        pipeline.set(
            name=TimetableRedisKeys.status.one(task_status.task_id),
            value=task_status.model_dump_json(),
            ex=CONSTANTS.redis_cache_expiry.timetable,
        )

        pipeline.set(
            name=TimetableRedisKeys.request.one(task_status.task_id),
            value=task_request.model_dump_json(),
            ex=CONSTANTS.redis_cache_expiry.timetable,
        )

        await pipeline.execute()

        # TODO HIER JOB IN DIE QUEUE LEGEN

    return task_status


async def set_timetable_task_solutions(redis: Redis, timetable_solution: TimetableTaskSolutions) -> None:
    """sets a solution to a timetable task in redis"""
    await redis.set(
        name=TimetableRedisKeys.solutions.one(timetable_solution.task_id),
        value=timetable_solution.model_dump_json(),
        ex=CONSTANTS.redis_cache_expiry.timetable,
    )


async def get_timetable_task_request(redis: Redis, task_id: UUID) -> TimetableTaskRequest:
    """retrieves a timetable task request"""
    data = await redis.get(TimetableRedisKeys.request.one(task_id))
    if not data:
        raise ObjectNotFoundException(task_id)
    return TimetableTaskRequest.model_validate_json(data)


async def get_timetable_task_status(redis: Redis, task_id: UUID) -> TimetableTaskStatus:
    """retrieves a timetable task status"""
    data = await redis.get(TimetableRedisKeys.status.one(task_id))
    if not data:
        raise ObjectNotFoundException(task_id)
    return TimetableTaskStatus.model_validate_json(data)


async def get_timetable_task_solutions(redis: Redis, task_id: UUID) -> TimetableTaskSolutions:
    """retrieves a timetable task solution"""
    data = await redis.get(TimetableRedisKeys.solutions.one(task_id))
    if not data:
        raise ObjectNotFoundException(task_id)
    return TimetableTaskSolutions.model_validate_json(data)


async def get_all_timetable_tasks_status(redis: Redis) -> list[TimetableTaskStatus]:
    """retrieves all timetable tasks status"""
    keys: list[str] = [key async for key in redis.scan_iter(TimetableRedisKeys.status.all())] # type: ignore
    if not keys:
        return []
    results = await redis.mget(keys)
    return [TimetableTaskStatus.model_validate_json(data) for data in results if data]


async def update_timetable_task_status(redis: Redis, task_status: TimetableTaskStatus) -> None:
    """updates the status if a timetable task in redis"""
    await redis.set(
        name=TimetableRedisKeys.status.one(task_status.task_id),
        value=task_status.model_dump_json(),
        ex=CONSTANTS.redis_cache_expiry.timetable,
    )
  

async def delete_timetable_task(redis: Redis, task_id: UUID) -> None:
    """deletes requests, status and solutions of a timetable task from redis"""
    async with redis.pipeline() as pipeline:
        pipeline.delete(TimetableRedisKeys.request.one(task_id))
        pipeline.delete(TimetableRedisKeys.status.one(task_id))
        pipeline.delete(TimetableRedisKeys.solutions.one(task_id))
        await pipeline.execute()