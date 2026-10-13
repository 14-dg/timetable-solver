from pydantic import BaseModel, Field

from core.solve.base_solution import BaseSolution


class SolverTaskSolutions(BaseModel):
    solutions: dict[int, BaseSolution] = Field(default={})


    def set_solution(self, solution: BaseSolution):
        self.solutions[] = solution