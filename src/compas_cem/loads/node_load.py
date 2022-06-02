from compas_cem.data import Data


__all__ = ["NodeLoad"]

# ==============================================================================
# Node Load
# ==============================================================================


class NodeLoad(Data):
    """
    A load defined by a position and a vector.

    Parameters
    ----------
    node : ``int``
        A node key
    vector : ``list`` of ``float``
        The load magnitude of the point load in xyz directions.
    """
    def __init__(self, node, vector=[0, 0, -1], **kwargs):
        super(NodeLoad, self).__init__(**kwargs)
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

    def __repr__(self):
        """
        """
        msg = "{0}(xyz={1!r}, load={2!r})"
        return msg.format(self.__class__.__name__, self.xyz, self.vector)

# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
