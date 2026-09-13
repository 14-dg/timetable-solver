from datetime import date

from pydantic import BaseModel


class SemesterSchema(BaseModel):
    id: int
    name: str
    start_date: date
    end_date: date