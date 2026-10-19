from abc import ABC

from pydantic import BaseModel


class BaseSolution(ABC, BaseModel):
    """
    Base Solution for all Solvers.
    """