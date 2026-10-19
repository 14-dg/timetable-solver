from uuid import UUID

from pydantic import BaseModel

from features.timetables.output_models.assignment import Assignment
from features.timetables.output_models.teacher_out import TeacherOut
from features.timetables.types import UniqueID


class LectureOut(BaseModel):
    id: UniqueID
    name: str
    teacher: TeacherOut
    assignments: list[Assignment]

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, LectureOut):
            return False
        return self.id == value.id


    def __hash__(self) -> int:
        if isinstance(self.id, UUID):
            return self.id.int
        return self.id