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

    # add constraints
    for constraint in constraints:
        optimizer.add_constraint(constraint)

    # add parameters
    for parameter in parameters:
        optimizer.add_parameter(parameter)

    start = time()
    form = optimizer.solve_nlopt(topology, algorithm, iters, eps)

    duration = time() - start
    penalty = optimizer.penalty
    evals = optimizer.evals

    return form, penalty, evals, duration


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    pass
