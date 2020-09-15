from nlopt import opt

from nlopt import LD_MMA
from nlopt import LN_COBYLA
from nlopt import LN_BOBYQA
from nlopt import LD_LBFGS
from nlopt import LD_SLSQP


__all__ = [
    "nlopt_algorithm",
    "nlopt_algorithms",
    "nlopt_solver"
]

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
    Currently supported algorithms are:
        - LD_MMA
        - LD_LBFGS
        - LD_SLSQP
        - LN_COBYLA
        - LN_BOBYQA

    For further information, please refer to nlopt's documentation.
    """
    algorithms = nlopt_algorithms()
    return algorithms[name]


def nlopt_algorithms():
    """
    A dictionary with all the supported NLOpt algorithms.
    """
    algorithms = {
        "LD_MMA": LD_MMA,
        "LD_LBFGS": LD_LBFGS,
        "LD_SLSQP": LD_SLSQP,
        "LN_COBYLA": LN_COBYLA,
        "LN_BOBYQA": LN_BOBYQA
    }
    return algorithms


def nlopt_solver(f, algorithm, dims, bounds_up, bounds_low, iters, stopval):
    """
    Wrapper around a typical NLOpt solver routine.
    """
    solver = opt(nlopt_algorithm(algorithm), dims)

    solver.set_lower_bounds(bounds_low)
    solver.set_upper_bounds(bounds_up)

    solver.set_maxeval(iters)
    solver.set_stopval(stopval)

    solver.set_min_objective(f)

    return solver
