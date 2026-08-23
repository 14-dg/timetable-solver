from pydantic import BaseModel
from types.room_type import RoomType
from types.event_type import EventType
from api.schemas.cohort import ApiCohort
from api.schemas.room import ApiRoom
from api.schemas.teacher import ApiTeacher

class ApiOccurenceRule(BaseModel):
    duration_slots: int # die dauer des termins in zeitslots
    week_step: int # alle wie viele wochen soll der termin stattfinden. 1 für jede woche, 2 für jede zweite woche
    week_offset: int # wenn die vorlesung alle 3 wochen stattfindet kann man hiermit sagen, ob die vorlesung in woche 1, 2 oder 3 stattfindet
    
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