from features.timetables.input_models.lecture_in import LectureIn
from features.timetables.output_models.timetable_solution import TimetableSolution


def assert_all_lectures_included(solution: TimetableSolution, leture_count: int):
    assert len(solution.lectures) == leture_count


def assert_all_lecture_occurences_included(solution: TimetableSolution, lectures: list[LectureIn]):
    for lec in lectures:
        assert len(solution.lectures[lec.id].assignments) == lec.times_per_week


def assert_no_overlap(solution: TimetableSolution, lectures: list[LectureIn]):
