from uuid import UUID


class SolverException(Exception):
    def __init__(
        self,
        task_id: UUID,
        message: str,
    ):
        self.task_id = task_id
        self.message = message