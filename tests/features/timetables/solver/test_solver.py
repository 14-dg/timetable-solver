import pytest

from features.timetables.input_models.lecture_in import LectureIn
from features.timetables.input_models.room_in import RoomIn
from features.timetables.input_models.teacher_in import TeacherIn


@pytest.fixture(name="feasible_problem")
def feasible_problem_mock():
    room_in = RoomIn(name="test_room", availability={1,2})
    teacher_in=TeacherIn(name="test_teacher", availability={1,2})
    lecture_in = LectureIn()

def test_feasible_problem(problem: TimetableProblem):
    pass