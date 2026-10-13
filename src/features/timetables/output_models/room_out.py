from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel

from features.timetables.types import UniqueID


@dataclass(frozen=True)
class RoomOut(BaseModel):
    id: UniqueID
    name: str


    def __eq__(self, value: object) -> bool:
        if not isinstance(value, RoomOut):
            return False
        return self.id == value.id


    def __hash__(self) -> int:
        if isinstance(self.id, UUID):
            return self.id.int
        return self.id