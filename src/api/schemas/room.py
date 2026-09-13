from pydantic import BaseModel
    
class RoomSchema(BaseModel):
    id: int
    name: str
    seats: int
    is_locked: bool
    accessible: bool