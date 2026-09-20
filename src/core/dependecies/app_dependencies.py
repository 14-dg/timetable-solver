from collections.abc import Callable
from typing import Any


class AppDependency:
    def __init__(self, on_create: Callable[..., Any], on_close: Callable[..., Any]):
        self.on_create = on_create
        self.on_close = on_close


    def create(self):
        self.dependency = self.on_create()


    def close(self):
        self.on_close()


class AppDependencies:
    def __init__(self, deps: list[AppDependency] | None):
        if deps:
            self.deps = deps
        else:
            self.deps = []


    def add_dependencys(self, deps: list[AppDependency]):
        self.deps.extend(deps)


    def add_dependency(self, dependency: AppDependency):
        self.deps.append(dependency)


    def create(self):
        for dep in self.deps:
            dep.create()


    def close(self):
        for dep in self.deps:
            dep.close()