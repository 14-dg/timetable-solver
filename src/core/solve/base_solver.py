from abc import ABC, abstractmethod

from core.tasks.solver_task_solutions import SolverTaskSolutions


class BaseSolver(ABC):

    @abstractmethod
    def solve(self) -> SolverTaskSolutions:
        raise NotImplementedError("Subclass needs to implement this!")