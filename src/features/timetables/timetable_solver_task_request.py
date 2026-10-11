from core.solve.solver_task_request import SolverTaskRequest
from features.timetables.input_models.timetable_problem import TimetableProblem


class TimetableSolverTaskRequest(SolverTaskRequest):
    problem_data: TimetableProblem