import compas

if compas.RHINO:
    from compas_rhino.geometry import RhinoLine

from compas_cem import Data


__all__ = ["Edge"]

# ==============================================================================
# Edge
# ==============================================================================


class Edge(Data):
    """
    The edge base class.
    """
    def __init__(self, u, v, **kwargs):
        self.u = u
        self.v = v
        self.attributes = {}

        kwargs = kwargs or {}
        self.attributes.update(kwargs)

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

    @classmethod
    def from_rhino_line(cls, rhino_line, **kwargs):
        """
        Create an edge from a rhino line.

        Parameters
        ----------
        rhino_line : ``Rhino.Geometry.Line``
            A rhino line.
        **kwargs : ``dict``
            Extra keyword arguments.

        Returns
        -------
        edge : ``Edge``
            An edge object.
        """
        line = RhinoLine.from_geometry(rhino_line).to_compas()
        return cls.from_line(line, **kwargs)

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
