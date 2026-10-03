from abc import ABC, abstractmethod

from core.solve.base_solution import BaseSolution


class BaseSolver(ABC):

    @abstractmethod
    def ready_for_solve(self) -> bool:
        raise NotImplementedError("Subclass needs to implement this!")


    @abstractmethod
    def solve(self) -> BaseSolution:
        raise NotImplementedError("Subclass needs to implement this!")