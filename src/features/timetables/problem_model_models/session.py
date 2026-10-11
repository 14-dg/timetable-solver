from dataclasses import dataclass

from features.timetables.input_models.time_grid import TimeGrid
from features.timetables.input_models.timetable_problem import TimetableProblem


@dataclass(frozen=True)
class Session:
    id: int
    lecture: int
    duration: int
    candidates: tuple[tuple[int, int], ...]   # (room_idx, start_slot)

    @staticmethod
    def valid_starts(avail: set[int], duration: int, grid: TimeGrid) -> set[int]:
        return {
            s for s in avail
            if s + duration - 1 < grid.n_slots
            and grid.day(s) == grid.day(s + duration - 1)
            and all(s + k in avail for k in range(duration))
        }

    @staticmethod
    def build_sessions(problem: TimetableProblem) -> list[Session]:
        for lecture in problem.lectures:

            room_candidates: list[] = []
            for room in problem.rooms:
                both_avail: set[int] = lecture.teacher.availability and room.availability