from dataclasses import dataclass
from enum import Enum

from models.occurence_rule import OccurenceRule

class RoomType(Enum):
    SEMINARRAUM = "seminarraum"
    LABOR = "labor"
    HOERSAAL = "hoersaal"
    PC_POOL = "pc_pool"

@dataclass(kw_only=True)
class Room:
    id: int
    name: str
    campus: str
    seats: int
    room_types: set[RoomType]
    equipment: set[str]

    availability_sessions: list[OccurenceRule]