from compas_cem.data import Data


__all__ = ["NodeSupport"]

# ==============================================================================
# Node Support
# ==============================================================================


class NodeSupport(Data):
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
    def __init__(self, node, **kwargs):
        super(NodeSupport, self).__init__(**kwargs)
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

    def __repr__(self):
        """
        """
        return "{0}(xyz={1!r})".format(self.__class__.__name__, self.xyz)

# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
