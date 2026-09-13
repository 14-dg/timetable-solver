from pydantic import BaseModel, Field
from datetime import date, time

class GridConfigSchema(BaseModel):
    days_per_week: int = 7
    slot_duration_minutes: int = 45
    day_start_time: time = time(8, 0)
    day_end_time: time = time(20, 0)

class SemesterSchema(BaseModel):
    id: int | None = None
    start_date: date | None = None
    end_date: date | None = None

class RoomSchema(BaseModel):
    id: int
    name: str
    seats: int
    is_locked: bool
    accessible: bool

class LecturerSchema(BaseModel):
    id: int
    name: str

class ApiOccurenceRule(BaseModel):
    duration_slots: int
    week_step: int
    week_offset: int

class FachsemesterSchema(BaseModel):
    course_of_study_id: int
    semester: int

class ApiLecture(BaseModel):
    id: int
    title: str
    long_name: str | None = None
    module_url: str | None = None
    type: str | None = None
    course_of_study_ids: list[int] = Field(default_factory=list[int])
    fachsemester: list[FachsemesterSchema] = Field(default_factory=list[FachsemesterSchema])
    lecturer_ids: list[int] = Field(default_factory=list[int])
    rules: list[ApiOccurenceRule] = Field(default_factory=list[ApiOccurenceRule])

class SolveRequestPayload(BaseModel):
    grid_config: GridConfigSchema
    semester: SemesterSchema
    rooms: list[RoomSchema]
    lecturers: list[LecturerSchema]
    lectures: list[ApiLecture]