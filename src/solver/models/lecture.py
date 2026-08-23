from dataclasses import dataclass

from models.cohort import Cohort
from models.room import Room, RoomType
from models.teacher import Teacher
from types.event_type import EventType

@dataclass(kw_only=True)
class ApiOccurenceRule:
    duration_slots: int # die dauer des termins in zeitslots
    week_step: int # alle wie viele wochen soll der termin stattfinden. 1 für jede woche, 2 für jede zweite woche
    week_offset: int # wenn die vorlesung alle 3 wochen stattfindet kann man hiermit sagen, ob die vorlesung in woche 1, 2 oder 3 stattfindet
    
@dataclass(kw_only=True)
class Lecture:
    id: int
    title: str
    event_type: EventType
    is_online: bool
    estimated_visitors: int

    occurence_rules: list[ApiOccurenceRule]

    teachers: list[Teacher]

    mandatory_for: list[Cohort] # pflichtfach für
    elective_for: list[Cohort] # wahlmodul für

    required_room_type: RoomType | None
    room_equipment_required: set[str]

    possible_rooms: list[Room] | None # die LV kann nur in einem dieser räume stattfinden
    preffered_rooms: list[Room] | None # die LV sollte am besten in einem dieser räume stattfinden
    impossible_rooms: list[Room] | None # die LV darf in keinem dieser räume stattfinden