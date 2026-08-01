import io
import pandas as pd
from ortools.sat.python import cp_model



def cp_sat_solver() -> None:
    # Data
    data_str = """
    worker  task  cost
      w1    t1    90
      w1    t2    80
      w1    t3    75
      w1    t4    70
      w2    t1    35
      w2    t2    85
      w2    t3    55
      w2    t4    65
      w3    t1   125
      w3    t2    95
      w3    t3    90
      w3    t4    95
      w4    t1    45
      w4    t2   110
      w4    t3    95
      w4    t4   115
      w5    t1    50
      w5    t2   110
      w5    t3    90
      w5    t4   100
    """

    data = pd.read_table(io.StringIO(data_str), sep=r"\s+")

    # Model
    model = cp_model.CpModel()

    # Variables
    x = model.new_bool_var_series(name="x", index=data.index)

    # Constraints
    # Each worker is assigned to at most one task.
    for unused_name, tasks in data.groupby("worker"):
        model.add_at_most_one(x[tasks.index])

    # Each task is assigned to exactly one worker.
    for unused_name, workers in data.groupby("task"):
        model.add_exactly_one(x[workers.index])

    # Objective
    model.minimize(data.cost.dot(x))

    # Solve
    solver = cp_model.CpSolver()
    status = solver.solve(model)

    # Print solution.
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f"Total cost = {solver.objective_value}\n")
        selected = data.loc[solver.boolean_values(x).loc[lambda x: x].index]
        for unused_index, row in selected.iterrows():
            print(f"{row.task} assigned to {row.worker} with a cost of {row.cost}")
    elif status == cp_model.INFEASIBLE:
        print("No solution found")
    else:
        print("Something is wrong, check the status and the log of the solve")