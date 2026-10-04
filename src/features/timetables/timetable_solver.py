from typing import final

from core.solve.base_solver import BaseSolver
from core.solve.solver_task_solutions import SolverTaskSolutions


@final
class TimetableSolver(BaseSolver):
    def __init__(self):
        pass
        

    def solve(self) -> SolverTaskSolutions:
        ...