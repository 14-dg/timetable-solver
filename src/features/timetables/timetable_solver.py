from typing import final

from ortools.sat.python import cp_model

from core.solve.base_solver import BaseSolver
from core.solve.solver_task_solutions import SolverTaskSolutions
from features.timetables.input_models.timetable_problem import TimetableProblem


@final
class TimetableSolver(BaseSolver):
    def __init__(
        self,
        problem_data: TimetableProblem,
    ) -> None:
        self._problem_data: TimetableProblem = problem_data
        self._model: cp_model.CpModel = self.build_model()
        self._solver = cp_model.CpSolver()

    def build_model(self) -> cp_model.CpModel:
        pass

    def solve(self) -> SolverTaskSolutions:
        pass