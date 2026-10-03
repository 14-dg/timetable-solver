from uuid import UUID

from pydantic import BaseModel, Field

from core.solve.base_solution import BaseSolution


class SolverTaskSolutions(BaseModel):
    task_id: UUID
    solutions: dict[int, BaseSolution] = Field(default={})