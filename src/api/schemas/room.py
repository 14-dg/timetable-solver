from datetime import datetime

from pydantic import BaseModel, Field

class BlockedRoomBookingSchema(BaseModel):
    room_id: int
    start_time: datetime
    end_time: datetime
    
class RoomSchema(BaseModel):
    id: int
    name: str
    seats: int
    room_type_id: str | None = None
    equipment_ids: list[str] = Field(default_factory=list)
    is_locked: bool
    accessible: bool