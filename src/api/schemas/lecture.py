from datetime import time

from pydantic import BaseModel, Field


class LectureTimeslotSchema(BaseModel):
    timeslot_id: int
    lecture_id: int
    lecture_title: str
    lecture_type: str | None = None
    course_of_study_ids: list[int] = Field(default_factory=list[int])
    fachsemester: list[int] = Field(default_factory=list[int])
    lecturer_ids: list[int] = Field(default_factory=list[int])
    
    room_id: int | None = None
    day_of_week: int
    start_time: time | None = None
    end_time: time | None = None
    week_skip: int = 0
    is_online: bool
    is_solver_pinned: bool