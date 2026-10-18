from dataclasses import dataclass

from features.timetables.output_models.room_out import RoomOut


@dataclass(frozen=True)
class Assignment:
    room: RoomOut
    start: int # der erste slot, der von diesem assignment belegt wird
    end: int # der letzte slot, der von der von diesem assignment belegt wird