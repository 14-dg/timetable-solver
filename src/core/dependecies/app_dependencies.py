from enum import Enum
from typing import Any, Protocol


class AppDependencies(Enum):
    REDIS_CLIENT="REDIS_CLIENT"
    REDIS_QUEUE="REDIS_QUEUE"


class AppDependency(Protocol):
    def create(self) -> Any: ...
    def get_value(self) -> Any: ...
    def close(self) -> Any: ...


class AppDependencyRepository:

    def __init__(self):
        self.dependencies: dict[AppDependencies, AppDependency] = {}

    def create_deps(self):
        for dep in vars(self).values():
            dep.create()


    def get(self, dep: AppDependencies) -> AppDependency:
        return self.dependencies[dep]


    def close_deps(self):
        for dep in self.dependencies.values():
            dep.close()