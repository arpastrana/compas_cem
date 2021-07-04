import compas

if compas.RHINO:
    from compas_rhino.geometry import RhinoPoint


__all__ = ["NodeSupport"]

# ==============================================================================
# Node Support
# ==============================================================================


class NodeSupport(object):
    """
    A support assigned to a node.

    Parameters
    ----------
    node : ``int``
        The key of the node where to apply the support to.

    Returns
    -------
    node_support : ``NodeSupport``
        A node support.
    """
    def __init__(self, node):
        self.node = node
        self.xyz = None

    @classmethod
    def from_point(cls, point):
        """
        Create a NodeSupport from a point.

        Parameters
        ----------
        point : ``list`` of ``float``
            The xyz coordinates of the positions where to assign a support.

        Returns
        -------
        support : ``NodeSupport``
            A support object.

        Notes
        -----
        The support will be assigned to a ``FormDiagram`` only if it has a node
        whose xyz coordinates matches defined by the ``NodeSupport``.
        Otherwise, the support will not be assigned to the diagram.
        """
        support = cls(node=None)
        support.xyz = point
        return support

    @classmethod
    def from_rhino_point(cls, rhino_point):
        """
        Create a NodeSupport from a rhino point.

        Parameters
        ----------
        point : ``Rhino.Geometry.Point3d``
            The xyz position where to apply a support.

        Returns
        -------
        support : ``NodeSupport``
            A support object.

        Notes
        -----
        The support will be assigned to a ``FormDiagram`` only if it has a node
        whose xyz coordinates matches defined by the ``NodeSupport``.
        Otherwise, the support will not be assigned to the diagram.
        """
        xyz = RhinoPoint.from_geometry(rhino_point).to_compas()
        return cls.from_point(xyz)


if __name__ == "__main__":
    pass
