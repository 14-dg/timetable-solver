from datetime import date

from pydantic import BaseModel


class SemesterSchema(BaseModel):
    id: int | None = None
    start_date: date | None = None
    end_date: date | None = None