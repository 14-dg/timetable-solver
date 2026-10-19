from abc import ABC

from pydantic import BaseModel, Field

from core.config.constants import CONSTANTS


class SolverParameters(ABC, BaseModel):
    """
    Generelle Parameter für ALLE Solver Klassen
    """
    timeout: int = Field(
        default=CONSTANTS.SOLVER_SETTINGS.DEFAULT_SOLVER_TIMEOUT,
        description="The time a Solver has to find a Solution.",
    )