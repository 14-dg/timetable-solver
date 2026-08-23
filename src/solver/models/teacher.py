from dataclasses import dataclass

@dataclass(kw_only=True)
class Teacher:
    id: int
    name: str
    max_hours_per_day: int | None
    max_consecutive_blocks: int | None

    available_slots: set[int]
    preffered_slots: set[int]