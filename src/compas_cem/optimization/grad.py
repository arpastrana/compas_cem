import numpy as np
# from autograd import grad as agrad
from jax import grad as agrad

__all__ = [
    "grad_finite_difference_numpy",
    "grad_autograd"
]


# ------------------------------------------------------------------------------
# Gradient calculation with finite differences
# ------------------------------------------------------------------------------

def grad_autograd(x, grad, x_func, verbose=False):
    """
    Automatic differentiation, baby.
    """
    grad_func = agrad(x_func)
    new_grad = grad_func(x)
    grad[:] = new_grad

    if verbose:
        print("====== Computing Gradient ======")
        print("Gradient: {}".format(grad))


# ------------------------------------------------------------------------------
# Gradient calculation with finite differences
# ------------------------------------------------------------------------------

def grad_finite_difference_numpy(x, grad, x_func, step_size, verbose=False):
    """
    Finite differences
    """
    # finite difference
    fx0 = x_func(x)

    for i in range(len(x)):  # vectorize with numpy?

        _x = np.copy(x)
        _x[i] += step_size

        fx1 = x_func(_x)

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
