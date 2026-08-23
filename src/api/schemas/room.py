from enum import Enum

from pydantic import BaseModel

from api.schemas.occurence_rule import ApiOccurenceRule

class RoomType(Enum):
    SEMINARRAUM = "seminarraum"
    LABOR = "labor"
    HOERSAAL = "hoersaal"
    PC_POOL = "pc_pool"


class ApiRoom(BaseModel):
    id: int
    name: str
    campus: str
    seats: int
    room_types: set[RoomType]
    equipment: set[str]

    availability_sessions: list[ApiOccurenceRule]