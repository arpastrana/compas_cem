from collections import namedtuple


def PointSupport(pos):
    """
    A point support.

    Parameters
    ----------
    pos : ``list`` of ``float``
        The position of the point support.

    Returns
    -------
    point_support : ``PointSupport``
        A point support.
    """
    support = namedtuple("PointSupport", ["position"])
    return support(pos)


if __name__ == "__main__":
    support = PointSupport([1.0, 0.0, 0,0])
    print(support)