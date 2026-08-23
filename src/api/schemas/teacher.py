from pydantic import BaseModel


class ApiTeacher(BaseModel):
    id: int
    name: str
    max_hours_per_day: int | None
    max_consecutive_blocks: int | None

    available_slots: set[int]
    preffered_slots: set[int]