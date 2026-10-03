from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

type TaskStatuses = Literal["Submitted", "Running", "Completed"]


class SolverTaskStatus(BaseModel):
    task_id: UUID = Field(default_factory=uuid4, description="The ID of the task.")
    status: TaskStatuses = Field(default="Submitted", description="The status of the task.")
    submitted_at: datetime = Field(default_factory=datetime.now, description="The time the task was submitted.")
    started_at: datetime | None = Field(default=None, description="The time the task was started.")
    completed_at: datetime | None = Field(default=None, description="The time the task was completed.")
    error: str | None = Field(default=None, description="The error message if the task failed.")