import json
from uuid import UUID

from redis.asyncio.client import Pipeline

from core.config.constants import CONSTANTS
from core.exceptions.crud_exceptions import ObjectNotFoundException
from features.timetables.schemas.timetable_redis_keys import TimetableRedisKeys
from features.timetables.schemas.timetable_task_request import TimetableTaskRequest
from features.timetables.schemas.timetable_task_solutions import TimetableTaskSolutions
from features.timetables.schemas.timetable_task_status import TimetableTaskStatus


async def create_timetable_task(pipeline: Pipeline, task_request: TimetableTaskRequest):
    """creates a timetable request and status in redis"""
    task_status = TimetableTaskStatus()

    await pipeline.set(
        name=TimetableRedisKeys.status.one(task_status.task_id),
        value=task_status.model_dump_json(),
        ex=CONSTANTS.redis_cache_expiry.timetable,
    )

    await pipeline.set(
        name=TimetableRedisKeys.request.one(task_status.task_id),
        value=task_request.model_dump_json(),
        ex=CONSTANTS.redis_cache_expiry.timetable,
    )

    return task_status


async def set_timetable_task_solutions(pipeline: Pipeline, timetable_solution: TimetableTaskSolutions):
    """sets a solution to a timetable task in redis"""
    await pipeline.set(
        name=TimetableRedisKeys.solutions.one(timetable_solution.task_id),
        value=timetable_solution.model_dump_json(),
        ex=CONSTANTS.redis_cache_expiry.timetable,
    )


async def get_timetable_task_request(pipeline: Pipeline, task_id: UUID):
    """retrieves a timetable task request"""
    data = await pipeline.get(TimetableRedisKeys.request.one(task_id))
    if not data:
        raise ObjectNotFoundException(task_id)
    return TimetableTaskRequest(**json.loads(data))

async def get_timetable_task_status(pipeline: Pipeline, task_id: UUID):
    """retrieves a timetable task status"""
    data = await pipeline.get(TimetableRedisKeys.status.one(task_id))
    if not data:
        raise ObjectNotFoundException(task_id)
    return TimetableTaskStatus(**json.loads(data))


async def get_timetable_task_solutions(pipeline: Pipeline, task_id: UUID):
    """retrieves a timetable task solution"""
    data = await pipeline.get(TimetableRedisKeys.solutions.one(task_id))
    if not data:
        raise ObjectNotFoundException(task_id)
    return TimetableTaskSolutions(**json.loads(data))


async def get_all_timetable_tasks_status(pipeline: Pipeline):
    """retrieves all timetable tasks status"""
    results = await pipeline.mget(TimetableRedisKeys.status.all())
    return [TimetableTaskStatus(**json.loads(data)) for data in results if data]


async def update_timetable_task_status(pipeline: Pipeline, task_status: TimetableTaskStatus):
    """updates the status if a timetable task in redis"""
    await pipeline.set(
        name=TimetableRedisKeys.status.one(task_status.task_id),
        value=task_status.model_dump_json(),
        ex=CONSTANTS.redis_cache_expiry.timetable,
    )

async def delete_timetable_task(pipeline: Pipeline, task_id: UUID):
    """deletes requests, status and solutions of a timetable task from redis"""
    await pipeline.delete(TimetableRedisKeys.request.one(task_id))
    await pipeline.delete(TimetableRedisKeys.status.one(task_id))
    await pipeline.delete(TimetableRedisKeys.solutions.one(task_id))