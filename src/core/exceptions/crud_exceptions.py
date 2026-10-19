from typing import Any

from core.exceptions.app_exception import AppException


class ObjectNotFoundException(AppException):

    id = "NO_ID_PROVIDED"
    code = "OBJECT_NOT_FOUND"
    message = "Object with supplied ID not found."

    def __init__(self, id: Any | None):
        if id: self.id = id

        super().__init__(
            message=self.message,
            code=self.code,
            details={"id": str(self.id)}
        )


class ObjectAlreadyExistsException(AppException):

    id = "NO_ID_PROVIDED"
    code = "OBJECT_ALREADY_EXISTS"
    message = "Object with supplied ID already exists."

    def __init__(self, id: Any | None):
        if id: self.id = id

        super().__init__(
            message=self.message,
            code=self.code,
            details={"id": str(self.id)}
        )