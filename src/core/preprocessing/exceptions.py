from typing import Any


class InfeasibleProblemException(Exception):
    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None
    ) -> None:
        self.message: str = message
        self.details: dict[str, Any] | None = details