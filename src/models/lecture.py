from dataclasses import dataclass


@dataclass(kw_only=True)
class Lecture:
    id: int
    name: str
    visitors: int

    def __str__(self) -> str:
        return f"{self.id=}\n{self.name=}\n{self.visitors=}\n"
        