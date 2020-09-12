from compas_rhino.geometry import RhinoPoint


class PointSupport(object):
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
    def __init__(self, pos):
        self.pos = pos

    @classmethod
    def from_rhino(cls, pos):
       """
       """
       pos = RhinoPoint.from_geometry(pos).to_compas()
       return cls(pos)


if __name__ == "__main__":
    support = PointSupport([1.0, 0.0, 0,0])
    print(support)