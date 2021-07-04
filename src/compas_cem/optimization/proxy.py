from time import time


__all__ = ["solve_nlopt_proxy"]


# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

def solve_nlopt_proxy(topology, constraints, parameters, algorithm, iters, eps):
    """
    Deprecated version of ``optimizer_solve_nlopt_proxy``.
    """
    from compas_cem.optimization import Optimizer

    optimizer = Optimizer()

    # add parameters
    for parameter in parameters:
        optimizer.add_goal(parameter)

    # add constraints
    for constraint in constraints:
        optimizer.add_constraint(constraint)

    start = time()
    form = optimizer.solve_nlopt(topology, algorithm, iters, eps)

    duration = time() - start
    x_opt = optimizer.parameters
    l_opt = optimizer.penalty
    evals = optimizer.evals

    return form, x_opt, l_opt, evals, duration


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    pass
