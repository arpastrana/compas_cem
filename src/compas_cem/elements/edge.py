from compas_cem.data import Data

__all__ = ["Edge"]

# ==============================================================================
# Edge
# ==============================================================================


class Edge(Data):
    """
    The base class shared by trail and deviation edges.

    Parameters
    ----------
    u :
        The key of the first node of the edge.
    v :
        The key of the second node of the edge.
    attrs :
        The attributes to store on the edge.

    Notes
    -----
    A node key here may also be a set of coordinates. A diagram resolves those
    to an existing node, or creates one, when the edge is added.
    """

    def __init__(self, u, v, attrs, **kwargs):
        super(Edge, self).__init__(**kwargs)

        self.u = u
        self.v = v
        self.attributes = attrs

        # kwargs = kwargs or {}
        # self.attributes.update(kwargs)

    @classmethod
    def from_line(cls, line, **kwargs):
        """
        Create an edge from a line described by two xyz coordinates.

        Parameters
        ----------
        line :
            The two end points of the line.
        **kwargs :
            Extra keyword arguments passed to the constructor.

        Returns
        -------
        edge :
            An edge whose two nodes are the end points of the line.
        """
        edge = cls(line[0], line[1], **kwargs)
        return edge

    def __iter__(self):
        """
        Iterates over the start and end nodes of an edge.

        Yields
        ------
        key :
            The next node key.
        """
        for node in (self.u, self.v):
            yield node


# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
