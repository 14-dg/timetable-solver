import logging
from dataclasses import dataclass
from typing import Self

from core.preprocessing.exceptions import InfeasibleProblemException
from features.timetables.input_models.lecture_in import LectureIn
from features.timetables.input_models.room_in import RoomIn
from features.timetables.input_models.time_grid_in import TimeGridIn
from features.timetables.input_models.timetable_problem import TimetableProblem

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PossibleLectureStarts:
    lecture_index: int
    # key = raum index, value = all valid start slots of a room for the lecture
    room_starts: dict[int, frozenset[int]]


    @staticmethod
    def _valid_starts(lecture: LectureIn, available: set[int], time_grid: TimeGridIn) -> frozenset[int]:
        last_offset: int = lecture.duration - 1
        return frozenset(
            start
            for start in available
            # checks that the lecture start slot and end slot are on the same day
            # therefore also checks that start and end are on the same week
            if time_grid.day(start) == time_grid.day(start + last_offset)
            # checks that slots exist for the entire duration of the lecture
            and all(start + k in available for k in range(lecture.duration))
        )


    @classmethod
    def _room_starts(cls, rooms: list[RoomIn], lecture: LectureIn, time_grid: TimeGridIn) -> dict[int, frozenset[int]]:
        # tmp for possible starts for a single lecture for multiple rooms
        room_starts: dict[int, frozenset[int]] = {}
        for room_index, room in enumerate(rooms):
            # slots that are available for the teacher and room
            mutually_available_slots: set[int] = lecture.teacher.availability & room.availability
            # valid start slots. room must be available for the duration of the lecture
            valid_starts: frozenset[int] = cls._valid_starts(lecture, mutually_available_slots, time_grid)
            if valid_starts:
                room_starts[room_index] = valid_starts
        return room_starts
        if not room_starts:
            raise InfeasibleProblemException(
                message=f"No possible rooms for lecture [{lecture.name}] [{lecture.id}] found.",
                details={
                    "lecture name": lecture.name,
                    "lecture id": lecture.id,
                },
            )
        return room_starts


    @classmethod
    def from_problem(cls, problem: TimetableProblem) -> list[Self]:
        result: list[Self] = []
        unplaceable: list[LectureIn] = []
        for lecture_index, lecture in enumerate(problem.lectures):
            room_starts: dict[int, frozenset[int]] = cls._room_starts(problem.rooms, lecture, problem.time_grid)
            if room_starts:
                result.append(cls(lecture_index, room_starts))
            else:
                unplaceable.append(lecture)

        if unplaceable:
            raise InfeasibleProblemException(
                message=f"{len(unplaceable)} lecture(s) cannot be placed in any room.",
                details={
                    "lectures": [
                        {"name": lec.name, "id": str(lec.id)} for lec in unplaceable
                    ]
                },
            )
        return result