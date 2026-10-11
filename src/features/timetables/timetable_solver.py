from typing import final

from core.solve.base_solver import BaseSolver
from core.solve.solver_task_solutions import SolverTaskSolutions
from features.timetables.input_models.timetable_problem import TimetableProblem


@final
class TimetableSolver(BaseSolver):
    def __init__(
        self,
        problem_model: TimetableProblem,
    ):
        pass
        

    def solve(self) -> SolverTaskSolutions:
        ...