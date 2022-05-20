import numpy as np

from autograd import grad as agrad


__all__ = ["grad_finite_differences_numpy",
           "grad_autograd"]

# ------------------------------------------------------------------------------
# Gradient calculation with finite differences
# ------------------------------------------------------------------------------


def grad_autograd(x, grad, grad_func):
    """
    Calculates the gradient with automatic differentiation. And updated grad in-place.
    """
    grad_func = agrad(grad_func)
    grad[:] = grad_func(x)

    return grad

# ------------------------------------------------------------------------------
# Gradient calculation with finite differences
# ------------------------------------------------------------------------------


def grad_finite_differences_numpy(x, grad, x_func, step_size):
    """
    Approximates the gradient of a blackbox function using finite differences.
    """
    # finite difference
    fx0 = x_func(x)

    for i in range(len(x)):  # vectorize with numpy?

        _x = np.copy(x)
        _x[i] += step_size

        fx1 = x_func(_x)  # bottleneck

        delta_fx = (fx1 - fx0) / step_size
        grad[i] = delta_fx

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------


if __name__ == "__main__":
    pass
