from typing import Any


class SolverTaskException(Exception):
    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.details: dict[str, Any] = details or {}


class InfeasibleProblemException(SolverTaskException):
    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            details=details
        )


class SolverSolutionException(SolverTaskException):
    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            details=details
        )