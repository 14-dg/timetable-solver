from dataclasses import dataclass
from models.types import timeframes


@dataclass(kw_only=True)
class Room:
    id: int
    seats: int
    available: timeframes

    def __str__(self) -> str:
        return f"{self.id=}\n{self.seats=}\n{self.available=}\n"