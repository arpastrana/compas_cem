import compas

if compas.RHINO:
    from compas_rhino.geometry import RhinoPoint


__all__ = ["Node"]

# ==============================================================================
# Node
# ==============================================================================


class Node(object):
    """
    A node.
    """
    def __init__(self, key=None, xyz=[0.0, 0.0, 0.0]):
        self.key = key
        self.xyz = xyz
        self.attributes = {}

    @classmethod
    def from_point(cls, point, *args, **kwargs):
        """
        Create a node from a point described by its xyz coordinates.

        Parameters
        ----------
        point : ``tuple`` or ``list``
            The xyz coordinates of the point.
        *args : ``tuple``
            Additional arguments.
        **kwargs : ``dict``
            Extra keyword arguments.

        Returns
        -------
        node : ``Node``
            A node object.
        """
        return cls(xyz=point)

    @classmethod
    def from_rhino_point(cls, rhino_point, *args, **kwargs):
        """
        Create a node from a rhino point.

        Parameters
        ----------
        rhino_point : ``Rhino.Geometry.Point3d``
            A rhino point.
        *args : ``tuple``
            Additional arguments.
        **kwargs : ``dict``
            Extra keyword arguments.

        Returns
        -------
        node : ``Node``
            A node object.
        """
        point = RhinoPoint.from_geometry(rhino_point).to_compas()
        return cls.from_point(point)

    def __repr__(self):
        """
        """
        return "{}(key={}, xyz={})".format(self.__class__.__name__, self.key, self.xyz)


if __name__ == "__main__":
    pass
