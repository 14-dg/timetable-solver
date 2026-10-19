from pydantic import BaseModel

from features.timetables.output_models.room_out import RoomOut


class Assignment(BaseModel):
    room: RoomOut
    start: int # der erste slot, der von diesem assignment belegt wird
    end: int # der letzte slot, der von diesem assignment belegt wird