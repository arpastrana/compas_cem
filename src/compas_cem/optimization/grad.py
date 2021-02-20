import numpy as np

# from jax import grad as agrad
from autograd import grad as agrad


__all__ = ["grad_finite_difference_numpy",
           "grad_autograd"]

# profiling stuff
import atexit
import line_profiler
profile = line_profiler.LineProfiler()
atexit.register(profile.print_stats)


# ------------------------------------------------------------------------------
# Gradient calculation with finite differences
# ------------------------------------------------------------------------------

def grad_autograd(x, grad, grad_func, verbose=False):
    """
    Automatic differentiation, baby.
    """
    if verbose:
        print("====== Computing Gradient ======")

    grad_func = agrad(grad_func)
    new_grad = grad_func(x)  # bottleneck
    grad[:] = new_grad

    if verbose:
        print("Gradient: {}".format(grad))

# ------------------------------------------------------------------------------
# Gradient calculation with finite differences
# ------------------------------------------------------------------------------

# @profile
def grad_finite_difference_numpy(x, grad, x_func, step_size, verbose=False):
    """
    Finite differences
    """
    # finite difference
    fx0 = x_func(x)

    for i in range(len(x)):  # vectorize with numpy?

        _x = np.copy(x)
        _x[i] += step_size

        fx1 = x_func(_x)  # bottleneck

        delta_fx = (fx1 - fx0) / step_size
        grad[i] = delta_fx

    if verbose:
        print("====== Computing Gradient ======")
        print("Gradient: {}".format(grad))


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    pass
