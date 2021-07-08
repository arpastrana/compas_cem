import compas

if compas.RHINO:
    from compas_rhino.geometry import RhinoPoint
    from compas_rhino.geometry import RhinoVector


__all__ = ["NodeLoad"]

# ==============================================================================
# Node Load
# ==============================================================================


class NodeLoad(object):
    """
    A load defined by a position and a vector.

    Parameters
    ----------
    node : ``int``
        A node key
    vector : ``list`` of ``float``
        The load magnitude of the point load in xyz directions.
    """
    def __init__(self, node, vector=[0, 0, -1]):
        self.node = node
        self.vector = vector
        self.xyz = None

    @classmethod
    def from_point_and_vector(cls, point, vector):
        """
        Create a NodeLoad from a point and a vector.

        Parameters
        ----------
        point : ``list`` of ``float``
            The xyz coordinates of the positions where to applied the load.
        vector : ``list`` of ``float``
            The xyz coordinates of the load vector.

        Returns
        -------
        load : ``NodeLoad``
            A load object.
        """
        load = cls(node=None, vector=vector)
        load.xyz = point
        return load

    @classmethod
    def from_rhino_point_and_vector(cls, rhino_point, rhino_vector):
        """
        Create a NodeLoad from a rhino point and a rhino vector.

        Parameters
        ----------
        rhino_point : ``Rhino.Geometry.Point``
            The load application point.
        rhino_vector : ``Rhino.Geometry.Vector3d``
            A vector that encodes the magnitude and direction of the load.

        Returns
        -------
        load : ``NodeLoad``
            A load object.
        """
        point = RhinoPoint.from_geometry(rhino_point).to_compas()
        vector = RhinoVector.from_geometry(rhino_vector).to_compas()
        return cls.from_point_and_vector(point, vector)


if __name__ == "__main__":
    pass
