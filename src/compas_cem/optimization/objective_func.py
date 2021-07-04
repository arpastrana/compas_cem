__all__ = ["objective_function_numpy"]


def objective_function_numpy(x, grad, x_func, grad_func):
    """
    """
    fx = x_func(x)

    if grad.size > 0:
        grad_func(x, grad)

    return fx

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------


if __name__ == "__main__":
    pass
