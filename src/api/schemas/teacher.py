from datetime import time

from pydantic import BaseModel

class LecturerAvailabilitySchema(BaseModel):
    lecturer_id: int
    day_of_week: int
    start_time: time
    end_time: time
    constraint_type: str  # z.B. 'hard' oder 'soft'

class LecturerSchema(BaseModel):
    id: int
    name: str
    department: str | None = None