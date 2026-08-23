from enum import Enum
from pydantic import BaseModel

from api.schemas.cohort import ApiCohort
from api.schemas.occurence_rule import ApiOccurenceRule
from api.schemas.room import ApiRoom, RoomType
from api.schemas.teacher import ApiTeacher



class EventType(Enum):
    VORLESUNG = "vorlesung"
    SEMINAR = "seminar"
    UEBUNG = "uebung"
    PRAKTIKUM = "praktikum"
    
class ApiLecture(BaseModel):
    id: int
    title: str
    event_type: EventType
    is_online: bool
    estimated_visitors: int

    start: int
    end: int
    sessions: list[ApiOccurenceRule]

    teachers: list[ApiTeacher]

    mandatory_for: list[ApiCohort] # pflichtfach für
    elective_for: list[ApiCohort]

    required_room_type: RoomType | None
    room_equipment_required: set[str]

    possible_rooms: list[ApiRoom] | None # die LV kann nur in einem dieser räume stattfinden
    preffered_rooms: list[ApiRoom] | None # die LV sollte am besten in einem dieser räume stattfinden
    impossible_rooms: list[ApiRoom] | None # die LV darf in keinem dieser räume stattfinden