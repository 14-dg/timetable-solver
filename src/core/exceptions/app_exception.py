from typing import Any


class AppException(Exception):

    def __init__(self, message: str, code: str, details: dict[str, Any]):
        self.code = code
        self.message = message
        self.details: dict[str, Any] = {}