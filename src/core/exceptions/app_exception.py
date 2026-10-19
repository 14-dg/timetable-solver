from typing import Any


class AppException(Exception):

    def __init__(
            self,
            message: str,
            code: str,
            headers: dict[str, str] | None = None,
            details: dict[str, Any] | None = None,
        ):
        self.headers = headers
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        return (f"Error: {self.code}\nMessage: {self.message}\n Details:\n {self.details}")