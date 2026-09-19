from uuid import UUID

from pydantic import BaseModel, Field


class TimetableTaskSolutions(BaseModel):
    task_id: UUID
    result_quality: str = Field(description="The Quality of the result the solver produced.")