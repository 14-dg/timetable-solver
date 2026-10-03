from enum import Enum
from uuid import UUID


class TaskClasses(Enum):
    REQUEST="request"
    SOLUTION="solution"
    STATUS="status"


class RedisKeyBundle:
    def __init__(self, base_key: str):
        self.base_key = base_key

    def all(self):
        return f"{self.base_key}:*"

    def one(self, id: UUID):
        return f"{self.base_key}:{id}"


class RedisKeys:
    request=RedisKeyBundle(TaskClasses.REQUEST.value)
    solutions=RedisKeyBundle(TaskClasses.SOLUTION.value)
    status=RedisKeyBundle(TaskClasses.STATUS.value)