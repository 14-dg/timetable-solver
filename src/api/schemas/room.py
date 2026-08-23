from pydantic import BaseModel

from types.room_type import RoomType
from types.weekday_type import Weekday

class RoomAvailabilityRule(BaseModel):
    week_offset: int
    week_step: int
    start: int
    end: int
    weekdays: list[Weekday]

class ApiRoom(BaseModel):
    id: int
    name: str
    campus: str
    seats: int
    room_types: set[RoomType]
    equipment: set[str]

    availability: list[RoomAvailabilityRule]