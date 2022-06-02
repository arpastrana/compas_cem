from compas_cem.data import Data


__all__ = ["Node"]

# ==============================================================================
# Node
# ==============================================================================


class Node(Data):
    """
    A node.
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

    def __repr__(self):
        """
        """
        return "{0!r}(key={1!r}, xyz={2!r})".format(self.__class__.__name__, self.key, self.xyz)

# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
