from typing import Any
from uuid import UUID


class SolverTaskException(Exception):
    def __init__(
        self,
        task_id: UUID,
        message: str,
        details: dict[str, Any] | None = None,
    ):
        self.task_id = task_id
        self.message = message
        self.details: dict[str, Any] | None = details


class PreproccessingException(SolverTaskException):
    def __init__(
            self,
    ):
        pass


class InfeasibleProblemException(SolverTaskException):
    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.details = details