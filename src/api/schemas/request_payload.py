from pydantic import BaseModel

from api.schemas.grid_config import GridConfigSchema
from api.schemas.room import RoomSchema
from api.schemas.semester import SemesterSchema
from api.schemas.teacher import LecturerSchema


class SolveRequestPayload(BaseModel):
    grid_config: GridConfigSchema
    semester: SemesterSchema
    rooms: list[RoomSchema]
    lecturers: list[LecturerSchema]
    lectures: list[Lecture]