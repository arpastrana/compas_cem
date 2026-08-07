from compas_cem.data import Data

__all__ = ["Node"]

# ==============================================================================
# Node
# ==============================================================================


class Node(Data):
    """
    A point in space that a diagram can be built around.

    Parameters
    ----------
    key :
        The key to register the node under. If `None`, the diagram assigns the
        next available key when the node is added.
    xyz :
        The coordinates of the node.
    """

    def __init__(self, key=None, xyz=[0.0, 0.0, 0.0], **kwargs):
        super(Node, self).__init__(**kwargs)
        self.key = key
        self.xyz = xyz
        self.attributes = {}

    @classmethod
    def from_point(cls, point, *args, **kwargs):
        """
        Create a node from a point described by its xyz coordinates.

        Parameters
        ----------
        point :
            The coordinates of the point.
        *args :
            Additional arguments, ignored.
        **kwargs :
            Extra keyword arguments, ignored.

        Returns
        -------
        node :
            A node with no key, sitting at the given point.
        """
        return cls(xyz=point)

    def __repr__(self):
        return "{0!r}(key={1!r}, xyz={2!r})".format(
            self.__class__.__name__, self.key, self.xyz
        )


# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
