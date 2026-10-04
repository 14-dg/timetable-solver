from enum import Enum
from typing import Literal
from uuid import UUID

from core.config.settings import SETTINGS


class TaskDataKeys(Enum):
    request="request"
    status="status"
    solutions="solutions"

type DomainType = Literal["timetable"]


class RedisKeys:
    def __init__(self, domain: DomainType):
        self._domain: DomainType = domain

    def task(self, id: UUID) -> str:
        return f"{SETTINGS.REDIS_KEY_PREFIX}:{self._domain}:task:{id}"

    def task_pattern(self):
        return f"{SETTINGS.REDIS_KEY_PREFIX}:{self._domain}:task:*"


# die key objekte für die features/domains
TIMETABLE_KEYS = RedisKeys("timetable")