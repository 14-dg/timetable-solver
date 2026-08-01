from dataclasses import dataclass
from models.types import availability

@dataclass(kw_only=True)
class Teacher:
    id: int
    name: str
    available: availability

    def __str__(self) -> str:
        return f"{self.id=}\n{self.name=}\n{self.available=}\n"
        