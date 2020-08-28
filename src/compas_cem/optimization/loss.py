import numpy as np


__all__ = [
    "norm_squared_error_numpy"
]


def norm_squared_error_numpy(y, y_hat):
    """
    Computes the squared sum of the row norms of ``y`` - ``y_hat``.

    Input
    -----
    y : ``np.array``
        An array with reference values.
    y_hat : ``np.array``
        An array with target values.

    Returns
    -------
    error : ``float``
        The squared sum of errors.
    """
    diff = y - y_hat
    sq_rownorms = np.square(np.linalg.norm(diff, axis=1))
    error = np.sum(sq_rownorms)
    return error


if __name__ == "__main__":
    from compas_cem.optimization import squared_error_numpy
