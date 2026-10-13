from datetime import UTC, datetime

from pydantic import Field

from core.solve.base_solution import BaseSolution
from features.timetables.output_models.lecture_out import LectureOut
from features.timetables.types import UniqueID


class TimetableSolution(BaseSolution):
    lectures: dict[UniqueID, LectureOut] = Field(description="The assignement of each lecture to a room")
    timestamp: datetime = Field(default_factory=lambda _: datetime.now(UTC), description="The time the solution was created.")