import numpy as np


__all__ = [
    "grad_finite_difference_numpy"
]

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
