from nlopt import opt

from nlopt import LD_AUGLAG
from nlopt import LD_LBFGS
from nlopt import LD_MMA
from nlopt import LD_SLSQP
from nlopt import LD_TNEWTON


__all__ = ["nlopt_algorithm",
           "nlopt_algorithms",
           "nlopt_solver",
           "nlopt_status"]


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
    Only the following local gradient-based optimization algorithms are supported:

    - SLSQP: Sequential Least Squares Programming
    - LBFGS: Low-Storage Broyden-Fletcher-Goldfarb-Shanno
    - AUGLAG: Augmented Lagrangian
    - MMA: Method of Moving Asymptotes
    - TNEWTON: Preconditioned Truncated Newton

    Refer to the NLopt `documentation <https://nlopt.readthedocs.io/en/latest/>`_ for more details on their theoretical underpinnings.
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

    Notes
    -----
    Only the following local gradient-based optimization algorithms are supported:

    - SLSQP: Sequential Least Squares Programming
    - LBFGS: Low-Storage Broyden-Fletcher-Goldfarb-Shanno
    - AUGLAG: Augmented Lagrangian
    - MMA: Method of Moving Asymptotes
    - TNEWTON: Preconditioned Truncated Newton

    Refer to the NLopt `documentation <https://nlopt.readthedocs.io/en/latest/>`_ for more details on their theoretical underpinnings.
    """
    algorithms = {}
    gradient_based = {"SLSQP": LD_SLSQP,
                      "MMA": LD_MMA,
                      "LBFGS": LD_LBFGS,
                      "AUGLAG": LD_AUGLAG,
                      "TNEWTON": LD_TNEWTON
                      }

    algorithms.update(gradient_based)

    return algorithms


def nlopt_status(constant):
    """
    Convert the number constant returned by the optimization process into a human-readable string.

    Input
    -----
    constant : ``int``
        The constant returned by the optimization algorithm as result.

    Returns
    -------
    status : ``str``
        A human-readable string.
    """
    results = {}

    success = {1: "NLOPT_SUCCESS",
               2: "NLOPT_EPSVAL_REACHED",
               3: "NLOPT_FTOL_REACHED",
               4: "NLOPT_XTOL_REACHED",
               5: "NLOPT_ITERSMAX_REACHED",
               6: "NLOPT_MAXTIME_REACHED"}

    failure = {-1: "NLOPT_GENERIC_FAILURE",
               -2: "NLOPT_INVALID_ARGS",
               -3: "NLOPT_OUT_OF_MEMORY",
               -4: "NLOPT_ROUNDOFF_LIMITED",
               -5: "NLOPT_FORCED_STOP"}

    results.update(success)
    results.update(failure)

    return results[constant]


def nlopt_solver(f, algorithm, dims, bounds_up, bounds_low, iters, eps, ftol):
    """
    Wrapper around a typical nlopt solver routine.
    """
    solver = opt(nlopt_algorithm(algorithm), dims)

    solver.set_lower_bounds(bounds_low)
    solver.set_upper_bounds(bounds_up)

    solver.set_maxeval(iters)

    if ftol is not None:
        solver.set_ftol_abs(ftol)  # abs per recommendation in the NLOpt docs

    if eps is not None:
        solver.set_stopval(eps)

    solver.set_min_objective(f)

    return solver
