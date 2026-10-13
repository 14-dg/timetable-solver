from dataclasses import dataclass

from features.timetables.output_models.room_out import RoomOut


@dataclass(frozen=True)
class Assignment:
    room: RoomOut
    start: int
    end: int