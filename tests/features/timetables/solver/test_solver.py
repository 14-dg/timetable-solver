import pytest

from core.solve.solver_exceptions import InfeasibleProblemException
from core.solve.solver_task_solutions import SolverTaskSolutions
from features.timetables.input_models.lecture_in import LectureIn
from features.timetables.input_models.room_in import RoomIn
from features.timetables.input_models.teacher_in import TeacherIn
from features.timetables.input_models.time_grid_in import TimeGridIn
from features.timetables.input_models.timetable_problem import TimetableProblem
from features.timetables.output_models.timetable_solution import TimetableSolution
from features.timetables.solver.timetable_solver import TimetableSolver


@pytest.fixture(name="feasible_problem")
def feasible_problem_mock():
    room_in = RoomIn(name="test_room", availability={0,1})
    teacher_in = TeacherIn(name="test_teacher", availability={0,1})
    math = LectureIn(name="math_test_lecture", times_per_week=1, duration=1, teacher=teacher_in)
    biology = LectureIn(name="biology_test_lecture", times_per_week=1, duration=1, teacher=teacher_in)
    time_grid_in = TimeGridIn(days=5, slots_per_day=10)
    return TimetableProblem(lectures=[math, biology], rooms=[room_in], time_grid=time_grid_in)


def test_feasible_problem(feasible_problem: TimetableProblem):
    solver = TimetableSolver(feasible_problem)
    solutions: SolverTaskSolutions = solver.solve()
    assert isinstance(solutions.solutions[0], TimetableSolution)


def test_infeasible_problem_teacher_conflict(feasible_problem: TimetableProblem):
    feasible_problem.lectures[0].teacher.availability = {1}
    with pytest.raises(InfeasibleProblemException):
        solver = TimetableSolver(feasible_problem)
        solver.solve()


def test_infeasible_problem_room_conflict(feasible_problem: TimetableProblem):
    # raum nur in einem slot verfügbar machen, da es 2 lectures gibt, sollte es einen fehler geben
    feasible_problem.rooms[0].availability = {1}
    with pytest.raises(InfeasibleProblemException):
        solver = TimetableSolver(feasible_problem)
        solver.solve()