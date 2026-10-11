from uuid import UUID


class SolverTaskException(Exception):
    def __init__(
        self,
        task_id: UUID,
        message: str,
    ):
        self.task_id = task_id
        self.message = message


class PreproccessingException(SolverTaskException):
    def __init__(
            self,
    ):
        pass