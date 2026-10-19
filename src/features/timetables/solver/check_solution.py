from core.solve.solver_exceptions import SolverSolutionException
from features.timetables.input_models.lecture_in import LectureIn
from features.timetables.input_models.room_in import RoomIn
from features.timetables.input_models.teacher_in import TeacherIn
from features.timetables.input_models.timetable_problem import TimetableProblem
from features.timetables.output_models.timetable_solution import TimetableSolution
from features.timetables.types import UniqueID


def assert_all_lecture_occurrences_included(solution: TimetableSolution, lectures_in: list[LectureIn]):
    for lec in lectures_in:
        lec_assign_len = len(solution.lectures[lec.id].assignments)
        if not lec_assign_len == lec.times_per_week:
            raise SolverSolutionException(f"""
                Demand not met for lecture [{lec.id}] {lec.name}:
                Number of lecture assignments {lec_assign_len} does not equal the demanded {lec.times_per_week} times
                """)


def assert_no_overlap(solution: TimetableSolution, problem: TimetableProblem):
    rooms_in: dict[UniqueID, RoomIn] = {room.id: room for room in problem.rooms}
    teachers_in: dict[UniqueID, TeacherIn] = {lecture.teacher.id: lecture.teacher for lecture in problem.lectures}


    rooms: dict[UniqueID, set[int]] = {}
    teachers: dict[UniqueID, set[int]] = {}

    for lec in solution.lectures.values():
        if not lec.teacher.id in teachers:
            teachers[lec.teacher.id] = teachers_in[lec.teacher.id].availability.copy()

        teacher_avail: set[int] = teachers[lec.teacher.id]

        for assignment in lec.assignments:
            if not assignment.room.id in rooms:
                rooms[assignment.room.id] = rooms_in[assignment.room.id].availability.copy()

            room_avail: set[int] = rooms[assignment.room.id]

            used_slots: set[int] = {i for i in range(assignment.start, assignment.end + 1)}
            used_slots_len = len(used_slots)

            room_avail_len = len(room_avail)
            teacher_avail_len = len(teacher_avail)

            room_avail -= used_slots
            teacher_avail -= used_slots

            # prüfen, dass used slots im room avail und teacher avail waren.
            # dafür muss die länge von avail_slots - länge von used_slots = die länge von avails_slots danmach sein
            if not room_avail_len - used_slots_len == len(room_avail):
                raise SolverSolutionException(f"""
                    Demand not met: Overlap in room [{assignment.room.id} {assignment.room.name}]
                """)
            if not teacher_avail_len - used_slots_len == len(teacher_avail):
                raise SolverSolutionException(f"""
                    Demand not met: Overlap for teacher [{lec.teacher.id} {lec.teacher.name}]
                """)