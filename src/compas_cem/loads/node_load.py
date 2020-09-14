from compas_rhino.geometry import RhinoPoint
from compas_rhino.geometry import RhinoVector


__all__ = [
    "NodeLoad"
]


class NodeLoad(object):
    """
    A load defined by a position and a vector.

    Parameters
    ----------
    node : ``int``
        A node key
    vector : ``list`` of ``float``
        The load magnitude of the point load in x, y, z directions in kN.
    """
    def __init__(self, node, vector=[0, 0, -1]):
        self.node = node
        self.vector = vector
        self.xyz = None

    @classmethod
    def from_point_and_vector(cls, point, vector):
       """
       """
       load = cls(node=None, vector=vector)
       load.xyz = point
       return load

    @classmethod
    def from_rhino_point_and_vector(cls, rhino_point, rhino_vector):
       """
       """
       point = RhinoPoint.from_geometry(rhino_point).to_compas()
       vector = RhinoVector.from_geometry(rhino_vector).to_compas()
       return cls.from_point_and_vector(point, vector)


if __name__ == "__main__":
    pass
