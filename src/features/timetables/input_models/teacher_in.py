from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from features.timetables.types import UniqueID


class TeacherIn(BaseModel):
    id: UniqueID = Field(description="Unique ID", default_factory=uuid4)
    name: str = Field(description="The name of the teacher")
    availability: set[int] = Field(
        description="The timeslots in during which the teacher is available for teaching.",
        min_length=1,
    )


    def __hash__(self) -> UniqueID:
        if isinstance(self.id, UUID):
            return self.id.int
        return self.id


    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, TeacherIn):
            return False
        return obj.id == self.id