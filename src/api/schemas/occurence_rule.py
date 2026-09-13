from pydantic import BaseModel

class OccurenceRule(BaseModel):
    duration_slots: int
    week_step: int
    week_offset: int