from math import copysign
from math import fabs

from compas_cem.elements import Edge


class TrailEdge(Edge):
    """
    An edge that advances a trail by a prescribed length.

    Parameters
    ----------
    u :
        The key of the first node of the edge.
    v :
        The key of the second node of the edge.
    length :
        The signed length of the edge. A negative value puts the edge in
        compression, and a positive value in tension.
    plane :
        A plane to intersect the trail with instead of advancing it by a fixed
        length.

    Notes
    -----
    A plane overrides the absolute length of the edge, but the sign of the
    length is preserved, so the combinatorial state survives the intersection.

    TODO: add an explicit combinatorial state to the signature of the constructor.
    """

    def __init__(self, u, v, length, plane=None, **kwargs):
        attrs = {"length": length, "type": "trail", "plane": plane}
        super(TrailEdge, self).__init__(u, v, attrs, **kwargs)
        # TODO
        # self.attributes = {"length": length, "state": state, type": "trail", "plane": plane}

    def __repr__(self):
        length = self.attributes["length"]
        msg = "{name}(length={length!r}, state={state!r}, plane={plane!r})"
        info = {
            "name": self.__class__.__name__,
            "length": fabs(length),
            "state": int(copysign(1, length)),
            "plane": self.attributes["plane"],
        }

        return msg.format(**info)


# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
