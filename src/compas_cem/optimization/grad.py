import numpy as np

from autograd import grad as agrad


__all__ = ["grad_finite_differences",
           "grad_autograd"]

# ------------------------------------------------------------------------------
# Gradient calculation with finite differences
# ------------------------------------------------------------------------------


def grad_autograd(x, grad, x_func, **kwargs):
    """
    Calculates the gradient with automatic differentiation. And updates grad in-place.
    """
    # TODO: Autograd function is re-built at every iteration. This is inefficient.
    # We can build it only once and then call it all subsequent times.
    # Thus, grad_func must become an input to this function instead of x_func.
    grad_func = agrad(x_func)
    grad[:] = grad_func(x)

    return grad

# ------------------------------------------------------------------------------
# Gradient calculation with finite differences
# ------------------------------------------------------------------------------


def grad_finite_differences(x, grad, x_func, step_size, **kwargs):
    """
    Approximates the gradient of a blackbox function using finite differences.
    """
    fx0 = x_func(x)
    # NOTE: Make an editable copy of x because NLOpt makes x a read-only vector
    _x = np.copy(x)

    for i in range(len(x)):

        _xi = _x[i]
        _x[i] += step_size

        fx1 = x_func(_x)

        delta_fx = (fx1 - fx0) / step_size
        grad[i] = delta_fx
        _x[i] = _xi

    return grad


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------


if __name__ == "__main__":
    pass
