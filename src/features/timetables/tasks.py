from uuid import UUID
from redis.asyncio import Redis


def run_timetable_task(
    task_id: UUID,
    redis: Redis,
) -> None:
