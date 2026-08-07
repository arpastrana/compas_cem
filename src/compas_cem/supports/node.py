from compas_cem.data import Data

__all__ = ["NodeSupport"]

# ==============================================================================
# Node Support
# ==============================================================================


class NodeSupport(Data):
    """
    A support that anchors one node of a diagram.

    Parameters
    ----------
    node :
        The key of the node to support.

    Notes
    -----
    Supports are where the trails of a topology diagram end. The form-finding
    algorithm walks back from every support to an origin node to build them.
    """

    def __init__(self, node, **kwargs):
        super(NodeSupport, self).__init__(**kwargs)
        self.node = node
        self.xyz = None

    @classmethod
    def from_point(cls, point):
        """
        Create a support from a point.

        Parameters
        ----------
        point :
            The coordinates of the position to support.

        Returns
        -------
        support :
            A support with no node key, positioned at the given point.

        Notes
        -----
        The support binds to a diagram node whose coordinates match the point.
        If no node sits there, the support is not assigned.
        """
        support = cls(node=None)
        support.xyz = point
        return support

    def __repr__(self):
        return "{0}(xyz={1!r})".format(self.__class__.__name__, self.xyz)


# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
