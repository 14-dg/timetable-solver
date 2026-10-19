from pydantic import BaseModel, Field, HttpUrl

from core.solve.solver_parameters import SolverParameters


class SolverTaskRequest(BaseModel):
    webhook_url: HttpUrl | None = Field(default=None, description="The URL to call once the computation is complete.")
    solver_parameters: SolverParameters = Field(description="The Parameters that are passed to the Solver.")