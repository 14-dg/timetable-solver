from pydantic import BaseModel, Field
from api.schemas.occurence_rule import OccurenceRule

class Lecture(BaseModel):
    id: int
    title: str
    type: str | None = None
    estimated_visitors: int
    lecturer_ids: list[int] = Field(default_factory=list[int])
    rules: list[OccurenceRule] = Field(default_factory=list[OccurenceRule])