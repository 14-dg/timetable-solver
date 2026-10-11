from datetime import UTC, datetime
from typing import TypedDict

from pydantic import Field

from core.solve.base_solution import BaseSolution


class LectureRoomMapping(TypedDict):
    ...


class TimetableSolution(BaseSolution):

    timestamp: datetime = Field(default_factory=lambda _: datetime.now(UTC), description="The time the solution was created.")