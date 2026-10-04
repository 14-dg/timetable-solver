from core.solve.solver_task_request import SolverTaskRequest
from features.timetables.timetable_problem import TimetableProblem


class TimetableSolverTaskRequest(SolverTaskRequest):
    problem_data: TimetableProblem