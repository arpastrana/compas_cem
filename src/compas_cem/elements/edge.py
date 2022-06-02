from compas_cem.data import Data


__all__ = ["Edge"]

# ==============================================================================
# Edge
# ==============================================================================


class Edge(Data):
    """
    The edge base class.
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
        line : ``tuple`` or ``list``
            The xyz coordinates of the line's two end points.
        **kwargs : ``dict``
            Extra keyword arguments.

        Returns
        -------
        edge : ``Edge``
            An edge object.
        """
        edge = cls(line[0], line[1], **kwargs)
        return edge

    def __iter__(self):
        """
        Iterates over the start and end nodes of an edge.

        Yields
        ------
        key : ``int``
            The next node key.
        """
        for node in (self.u, self.v):
            yield node

# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
