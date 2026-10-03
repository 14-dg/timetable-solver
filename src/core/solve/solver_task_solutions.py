from uuid import UUID

from pydantic import BaseModel


class SolverTaskSolutions(BaseModel):
    task_id: UUID
    