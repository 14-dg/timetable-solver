from abc import ABC

from pydantic import BaseModel


class BaseSolution(ABC, BaseModel):
    pass