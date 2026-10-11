import pytest

from core.preprocessing.exceptions import InfeasibleProblemException
from features.timetables.input_models.lecture import Lecture
from features.timetables.input_models.room import Room
from features.timetables.input_models.teacher import Teacher
from features.timetables.input_models.time_grid import TimeGrid
from features.timetables.input_models.timetable_problem import TimetableProblem
from features.timetables.problem_model_models.possible_lecture_starts import (
    PossibleLectureStarts,
)


def make_problem(
    teacher_slots: set[int],
    rooms_slots: list[set[int]],
    duration: int,
    slots_per_day: int = 4,
) -> TimetableProblem:
    teacher = Teacher(name="alice", availability=teacher_slots)
    lecture = Lecture(name="lec", times_per_week=1, duration=duration, teacher=teacher)
    rooms: list[Room] = [Room(name=f"r{i}", availability=s) for i, s in enumerate(rooms_slots)]
    return TimetableProblem(
        lectures=[lecture],
        rooms=rooms,
        time_grid=TimeGrid(days=5, slots_per_day=slots_per_day),
    )


def test_start_must_be_available_for_teacher_and_room():
    problem: TimetableProblem = make_problem({0, 1, 2, 3}, [{0, 1, 2, 4, 5, 6}], duration=3)
    starts: list[PossibleLectureStarts] = PossibleLectureStarts.from_problem(problem)
    assert starts[0].room_starts == {0: {0}}


def test_lecture_cannot_cross_day_boundary():
    everything: set[int] = set(range(8))
    problem: TimetableProblem = make_problem(everything, [everything], duration=2)
    starts: list[PossibleLectureStarts] = PossibleLectureStarts.from_problem(problem)
    assert starts[0].room_starts[0] == {0, 1, 2, 4, 5, 6}  # 3 und 7 laufen über die Tagesgrenze


def test_room_without_valid_start_is_omitted():
    teacher_slots: set[int] = {0, 1, 2}
    problem: TimetableProblem = make_problem(teacher_slots, [{5, 6}, {0, 1, 2}], duration=2)
    starts: list[PossibleLectureStarts] = PossibleLectureStarts.from_problem(problem)
    assert set(starts[0].room_starts) == {1}


def test_no_common_availability_raises():
    problem: TimetableProblem = make_problem({0, 1, 2, 3}, [{4, 5, 6}], duration=3)
    with pytest.raises(InfeasibleProblemException):
        PossibleLectureStarts.from_problem(problem)