from time import time


__all__ = ["solve_nlopt_proxy"]


# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

def solve_nlopt_proxy(topology, constraints, parameters, algorithm, iters, eps=None, tmax=100, eta=1e-6):
    """
    Solve a constrained form-finding task through a Proxy server hyperspace tunnel.

    Parameters
    ----------
    topology : :class:`compas_cem.diagrams.TopologyDiagram`
        A topology diagram.
    constraints : ``list``
        A list with the constraints to optimize for.
    parameters : ``list``
        A list of optimization parameters.
    algorithm : ``str``
        The name of the gradient-based local optimization algorithm to use.
        Only the following local gradient-based optimization algorithms are supported:

        - SLSQP: Sequential Least Squares Programming
        - LBFGS: Low-Storage Broyden-Fletcher-Goldfarb-Shanno
        - AUGLAG: Augmented Lagrangian
        - MMA: Method of Moving Asymptotes
        - TNEWTON: Preconditioned Truncated Newton

        Refer to the NLopt `documentation <https://nlopt.readthedocs.io/en/latest/>`_ for more details on their theoretical underpinnings.
    iters : ``int``
        The maximum number of iterations to run the optimization algorithm for.
    eps : ``float``
        The numerical convergence threshold for the optimization algorithm.
        If value is set to ``None``, this parameter is ignored and the
        optimization algorithm will run until ``iters`` is exhausted.
        Defaults to ``None``.
    tmax : ``int``, optional
        The maximum number of iterations the CEM form-finding algorithm will run for.
        If ``eta`` is hit first, the form-finding algorithm will stop early.
        Defaults to ``100``.
    eta : ``float``, optional
        The numerical converge threshold of the CEM form-finding algorithm.
        If ``tmax`` is hit first, the form-finding algorithm will stop early.
        Defaults to ``1e-6``.

    Returns
    -------
    form : :class:`compas_cem.diagrams.FormDiagram`
        A form diagram.
    objective : `float`
        The final value of the objective function.
    grad_norm : `float`
        The cummulative norm of the gradients.
    iters : `int`
        The elapsed number of iterations.
    duration : `float`
        The total optimization time in milliseconds.
    status : `str`
        The final status of the optimization problem as per NLOpt.
    """
    # TODO: the optimizer import statement should be handled more elegantly
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

    duration = round(time() - start, 2)
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
