from dataclasses import dataclass
from enum import Enum

from models.cohort import Cohort
from models.room import Room, RoomType
from models.teacher import Teacher

class EventType(Enum):
    VORLESUNG = "vorlesung"
    SEMINAR = "seminar"
    UEBUNG = "uebung"
    PRAKTIKUM = "praktikum"
    
@dataclass(kw_only=True)
class Lecture:
    id: int
    title: str
    event_type: EventType
    is_online: bool
    estimated_visitors: int

    slots: set[int]

    teachers: list[Teacher]

    mandatory_for: list[Cohort] # pflichtfach für
    elective_for: list[Cohort] # wahlmodul für

    required_room_type: RoomType | None
    room_equipment_required: set[str]

    possible_rooms: list[Room] | None # die LV kann nur in einem dieser räume stattfinden
    preffered_rooms: list[Room] | None # die LV sollte am besten in einem dieser räume stattfinden
    impossible_rooms: list[Room] | None # die LV darf in keinem dieser räume stattfinden