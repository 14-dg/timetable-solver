from pydantic import BaseModel

from api.schemas.constraints import ConstraintsSchema
from api.schemas.grid_config import GridConfigSchema
from api.schemas.lecture import LectureTimeslotSchema
from api.schemas.room import BlockedRoomBookingSchema, RoomSchema
from api.schemas.semester import SemesterSchema
from api.schemas.teacher import LecturerAvailabilitySchema, LecturerSchema


class SolveRequestPayload(BaseModel):
    institution_id: str
    semester: SemesterSchema
    target_course_of_study_ids: list[int] # für welche courses of study (studiengänge) gesolved werden soll
    grid_config: GridConfigSchema
    
    rooms: list[RoomSchema]
    lecturers: list[LecturerSchema]
    lecture_timeslots: list[LectureTimeslotSchema]
    lecturer_availability: list[LecturerAvailabilitySchema]
    blocked_room_bookings: list[BlockedRoomBookingSchema]
    
    constraints: ConstraintsSchema
    lecture_type_workload: dict[str, float]