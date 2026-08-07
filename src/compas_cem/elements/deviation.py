from math import copysign
from math import fabs

from compas_cem.elements import Edge


class DeviationEdge(Edge):
    """
    An edge that carries a prescribed force between two trails.

    Parameters
    ----------
    u :
        The key of the first node of the edge.
    v :
        The key of the second node of the edge.
    force :
        The signed force in the edge. A negative value puts the edge in
        compression, and a positive value in tension.

    Notes
    -----
    A deviation edge is direct when both of its nodes belong to the same
    sequence, and indirect otherwise. That distinction is drawn from the
    topology diagram rather than from the edge itself.
    """

    def __init__(self, u, v, force, **kwargs):
        attrs = {"force": force, "type": "deviation"}
        super(DeviationEdge, self).__init__(u, v, attrs, **kwargs)

    def __repr__(self):
        force = self.attributes["force"]
        msg = "{name}(force={force!r}, state={state!r})"
        info = {
            "name": self.__class__.__name__,
            "force": fabs(force),
            "state": int(copysign(1, force)),
        }

        return msg.format(**info)


# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
