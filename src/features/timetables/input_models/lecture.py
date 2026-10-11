from uuid import uuid4

from pydantic import BaseModel, Field

from features.timetables.input_models.teacher import Teacher
from features.timetables.types import UniqueID


class Lecture(BaseModel):
    id: UniqueID = Field(default_factory=uuid4)
    name: str = Field(description="The name of the lecture")
    times_per_week: int = Field(
        description="The amount of times the lecture needs to be held per week",
        ge=1,
        le=7,
    )
    duration: int = Field(
        description="The duration in consecutive timeslots one lecture instance takes",
        ge=1,
    )
    teacher: Teacher = Field(description="The Teacher who teaches the lecture")