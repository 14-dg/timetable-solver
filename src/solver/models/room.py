from dataclasses import dataclass
from enum import Enum

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

    slots: set[int]