from time import time


__all__ = ["solve_nlopt_proxy"]


# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

def solve_nlopt_proxy(form, goals, constraints, algorithm, iters, step_size, stop_val, mode):
    """
    Deprecated version of ``optimizer_solve_nlopt_proxy``.
    """
    from compas_cem.optimization import Optimizer

    optimizer = Optimizer()

    # add goals
    for goal in goals:
        optimizer.add_goal(goal)
    
    # add constraints
    for constraint in constraints:
        optimizer.add_constraint(constraint)

    start = time()
    x_opt, l_opt = optimizer.solve_nlopt(form, algorithm, iters, step_size, stop_val, mode=mode)
    duration = time() - start

    return form, x_opt, l_opt, duration

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    pass
