import json
from typing import Any, cast
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from core.solve.solver_task_request import SolverTaskRequest
from core.solve.solver_task_solutions import SolverTaskSolutions
from core.solve.solver_task_status import SolverTaskStatus


class TaskData(BaseModel):
    task_id: UUID = Field(default_factory=uuid4, description="The ID of the task.")
    request: SolverTaskRequest
    status: SolverTaskStatus = Field(default_factory=SolverTaskStatus)
    solutions: SolverTaskSolutions = Field(default_factory=SolverTaskSolutions)


    @model_validator(mode='before')
    @classmethod
    def parse_redis_json_strings(cls, data: Any) -> Any:
        """Parst JSON-Strings aus Redis-Hashes in Dictionaries, bevor Pydantic validiert."""
        if isinstance(data, dict):
            typed_data: dict[str, Any] = cast(dict[str, Any], data)
            parsed: dict[str, Any] = dict(typed_data)
            for field in ['request', 'status', 'solutions']:
                if field in parsed and isinstance(parsed[field], str):
                    parsed[field] = json.loads(parsed[field])
            return parsed
        return data