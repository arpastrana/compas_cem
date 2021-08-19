from time import time


__all__ = ["solve_nlopt_proxy"]


# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

def solve_nlopt_proxy(topology, constraints, parameters, algorithm, iters, eps, tmax=100, eta=1e-6):
    """
    Solve a constrained form-finding task through a Proxy server.
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
    form = optimizer.solve_nlopt(topology, algorithm, iters, eps, tmax, eta)

    duration = time() - start
    objective = optimizer.penalty
    evals = optimizer.evals
    grad_norm = optimizer.gradient_norm
    status = optimizer.status

    return form, objective, grad_norm, evals, duration, status

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------


if __name__ == "__main__":
    pass
