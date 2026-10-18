from collections import defaultdict
from typing import final

from ortools.sat.python import cp_model
from ortools.sat.python.cp_model_helper import CpSolverStatus

from core.solve.base_solver import BaseSolver
from core.solve.solver_exceptions import InfeasibleProblemException
from core.solve.solver_task_solutions import SolverTaskSolutions
from features.timetables.input_models.lecture_in import LectureIn
from features.timetables.input_models.room_in import RoomIn
from features.timetables.input_models.timetable_problem import TimetableProblem
from features.timetables.output_models.assignment import Assignment
from features.timetables.output_models.lecture_out import LectureOut
from features.timetables.output_models.room_out import RoomOut
from features.timetables.output_models.teacher_out import TeacherOut
from features.timetables.output_models.timetable_solution import TimetableSolution
from features.timetables.problem_models.possible_lecture_starts import (
    PossibleLectureStarts,
)
from features.timetables.solver.check_solution import (
    assert_all_lecture_occurences_included,
    assert_no_overlap,
)
from features.timetables.types import UniqueID

VarKey = tuple[int, int, int, int]


@final
class TimetableSolver(BaseSolver):
    def __init__(
        self,
        problem_data: TimetableProblem,
    ) -> None:
        self._problem: TimetableProblem = problem_data
        self._solver = cp_model.CpSolver()
        self._possible_lecture_starts: list[PossibleLectureStarts] = PossibleLectureStarts.from_problem(self._problem)
        self._x: dict[VarKey, cp_model.IntVar] = {}
        self._model: cp_model.CpModel = self.build_model()

    def build_model(self) -> cp_model.CpModel:
        model = cp_model.CpModel()
        by_occurrence: dict[tuple[int, int], list[cp_model.IntVar]] = defaultdict(list)
        by_teacher_slot: dict[tuple[object, int], list[cp_model.IntVar]] = defaultdict(list)
        by_room_slot: dict[tuple[int, int], list[cp_model.IntVar]] = defaultdict(list)

        for possible in self._possible_lecture_starts:
            lecture_index = possible.lecture_index
            lecture = self._problem.lectures[lecture_index]
            for occurrence in range(lecture.times_per_week):
                for room_index, starts in possible.room_starts.items():
                    for start in sorted(starts):
                        key = (lecture_index, occurrence, room_index, start)
                        var = model.new_bool_var(f"x_l{lecture_index}_k{occurrence}_r{room_index}_s{start}")
                        self._x[key] = var
                        by_occurrence[(lecture_index, occurrence)].append(var)
                        for slot in range(start, start + lecture.duration):
                            by_teacher_slot[(lecture.teacher.id, slot)].append(var)
                            by_room_slot[(room_index, slot)].append(var)

        for variables in by_occurrence.values():
            model.add_exactly_one(variables)
        for variables in by_teacher_slot.values():
            model.add_at_most_one(variables)
        for variables in by_room_slot.values():
            model.add_at_most_one(variables)

        return model


    def build_solution(self) -> TimetableSolution:
        output_lectures: dict[UniqueID, LectureOut] = {}
        output_rooms: dict[UniqueID, RoomOut] = {}
        output_teachers: dict[UniqueID, TeacherOut] = {
            lec.teacher.id: TeacherOut(id=lec.teacher.id, name=lec.teacher.name)
            for lec in self._problem.lectures
        }
        for key, val in self._x.items():
            if self._solver.value(val) == 1:
                lecture_i, _, room_i, start = key
                lecture_input: LectureIn = self._problem.lectures[lecture_i]
                room_input: RoomIn = self._problem.rooms[room_i]

                # output room objekt erstellen und speichern
                if room_input.id in output_rooms:
                    output_room: RoomOut = output_rooms[room_input.id]
                else:
                    output_room = RoomOut(id=room_input.id, name=room_input.name)
                    output_rooms[room_input.id] = output_room
                
                if lecture_input.id in output_lectures:
                    lecture_out: LectureOut = output_lectures[lecture_input.id]
                    lecture_out.assignments.append(
                        Assignment(output_room, start=start, end=start+lecture_input.duration)
                    )

                else:
                    lecture_out = LectureOut(
                        id=lecture_input.id,
                        name=lecture_input.name,
                        teacher=output_teachers[lecture_input.teacher.id],
                        assignments=[
                            Assignment(output_room, start=start, end=start+lecture_input.duration - 1)
                        ]
                    )
                    output_lectures[lecture_out.id] = lecture_out

        return TimetableSolution(lectures=output_lectures)


    def check_solution(self, solution: TimetableSolution, problem: TimetableProblem):
        assert_all_lecture_occurences_included(solution, problem.lectures)
        assert_no_overlap(solution, self._problem)


    def solve(self) -> SolverTaskSolutions:
        self._solver.parameters.max_time_in_seconds = 30.0
        status: CpSolverStatus = self._solver.solve(self._model)

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            solution: TimetableSolution = self.build_solution()

            self.check_solution(solution, self._problem)

            return SolverTaskSolutions(
                solutions={
                    0: solution
                }
            )

        if status == cp_model.INFEASIBLE:

            raise InfeasibleProblemException(
                message="No timetable satisfies all constraints.", details={}
            )
        raise RuntimeError(f"Solver stopped without result: {self._solver.status_name(status)}")