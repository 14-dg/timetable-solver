from pydantic import BaseModel, Field

from core.solve.base_solution import BaseSolution


class SolverTaskSolutions[T: BaseSolution](BaseModel):
    
    solutions: dict[int, T] = Field(default={})


    def set_solution(self, solutions: T):
        self.solutions[len(self.solutions)] = solutions