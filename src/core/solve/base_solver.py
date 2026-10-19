from abc import ABC, abstractmethod

from core.solve.base_solution import BaseSolution
from core.solve.solver_task_solutions import SolverTaskSolutions


class BaseSolver[T: BaseSolution](ABC):

    @abstractmethod
    def solve(self) -> SolverTaskSolutions[T]:
        """
        Raises:
            SolverError
        """
        raise NotImplementedError("Subclass needs to implement this!")