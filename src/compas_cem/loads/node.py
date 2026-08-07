from compas_cem.data import Data

__all__ = ["NodeLoad"]

# ==============================================================================
# Node Load
# ==============================================================================


class NodeLoad(Data):
    """
    A point load applied to one node of a diagram.

    Parameters
    ----------
    node :
        The key of the node to load.
    vector :
        The xyz components of the load. Defaults to one unit downwards.
    """

    def __init__(self, node, vector=[0.0, 0.0, -1.0], **kwargs):
        super(NodeLoad, self).__init__(**kwargs)
        self.node = node
        self.vector = vector
        self.xyz = None

    @classmethod
    def from_point_and_vector(cls, point, vector):
        """
        Create a load from a point and a vector.

        Parameters
        ----------
        point :
            The coordinates of the position where the load is applied.
        vector :
            The xyz components of the load.

        Returns
        -------
        load :
            A load with no node key, positioned at the given point.

        Notes
        -----
        The load binds to a diagram node whose coordinates match the point. If
        no node sits there, the load is not assigned.
        """
        load = cls(node=None, vector=vector)
        load.xyz = point
        return load

    def __repr__(self):
        msg = "{0}(xyz={1!r}, load={2!r})"
        return msg.format(self.__class__.__name__, self.xyz, self.vector)


# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
