from compas_rhino.geometry import RhinoPoint
from compas_rhino.geometry import RhinoVector


class PointLoad(object):
    """
    A load defined by a position and a vector.

    Parameters
    ----------
    pos : ``list`` of ``float``
        The load's application point.
    vector : ``list`` of ``float``
        The load magnitude of the point load in x, y, z directions in kN.

    Returns
    -------
    point_load : ``PointLoad``
        A point load.
    """

    def __init__(self, pos, vector=[0, 0, -1]):
        self.pos = pos
        self.vec = vector


    @classmethod
    def from_rhino(cls, pos, vector):
       """
       """
       pos = RhinoPoint.from_geometry(pos).to_compas()
       vector = RhinoVector.from_geometry(vector).to_compas()

       return cls(pos, vector)


if __name__ == "__main__":
    pass
