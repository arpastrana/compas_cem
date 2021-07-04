from nlopt import opt

from nlopt import LD_AUGLAG
from nlopt import LD_LBFGS
from nlopt import LD_MMA
from nlopt import LD_SLSQP
from nlopt import LD_TNEWTON

from nlopt import LN_BOBYQA
from nlopt import LN_COBYLA
from nlopt import LN_SBPLX


__all__ = ["nlopt_algorithm",
           "nlopt_algorithms",
           "nlopt_solver"]


def nlopt_algorithm(name):
    """
    Fetches an optimization algorithm from the nlopt library by name.

    Parameters
    ----------
    name : ``str``
        The name of the algorithm to search for.

    Returns
    -------
    algorithm : ``nlopt.algorithm``
        An nlopt algorithm object.

    Notes
    -----
    Only the following local optimization algorithms are supported:

    Gradient-based:

        - LD_MMA
        - LD_LBFGS
        - LD_AUGLAG
        - LD_SLSQP
        - LD_TNEWTON

    Derivative-free:

        - LN_BOBYQA
        - LN_COBYLA
        - LN_SBPLX

    Refer to nlopt's docs for more details on their theoretical underpinnings.
    """

    algorithms = nlopt_algorithms()
    return algorithms[name]


def nlopt_algorithms():
    """
    A dictionary with all the supported nlopt algorithms.

    Returns
    -------
    algorithms : ``dict``
        A dictionary that maps algorithm names to nlopt algorithm objects.
    """
    algorithms = {}

    gradient_based = {
        "LD_MMA": LD_MMA,  # Method of moving asymptotes
        "LD_LBFGS": LD_LBFGS,  # Low-storage BFGS
        "LD_AUGLAG": LD_AUGLAG,  # Augmented lagrangian algorithm
        "LD_SLSQP": LD_SLSQP,  # Sequential quadratic programming algorithm
        "LD_TNEWTON": LD_TNEWTON,  # Preconditioned truncated Newton
    }

    derivative_free = {
        "LN_BOBYQA": LN_BOBYQA,  # BOBYQA
        "LN_COBYLA": LN_COBYLA,  # Constrained optimization by linear approx
        "LN_SBPLX": LN_SBPLX,  # Tom Rowan's "Subplex" algorithm
    }

    algorithms.update(derivative_free)
    algorithms.update(gradient_based)

    return algorithms


def nlopt_solver(f, algorithm, dims, bounds_up, bounds_low, iters, stopval, ftol):
    """
    Wrapper around a typical nlopt solver routine.
    """
    solver = opt(nlopt_algorithm(algorithm), dims)

    solver.set_lower_bounds(bounds_low)
    solver.set_upper_bounds(bounds_up)

    solver.set_maxeval(iters)

    if ftol is not None:
        solver.set_ftol_abs(ftol)  # abs per recommendation

    if stopval is not None:
        solver.set_stopval(stopval)

    solver.set_min_objective(f)

    return solver
