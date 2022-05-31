from math import fabs
from math import copysign

from compas_cem.elements import Edge


class DeviationEdge(Edge):
    """
    A deviation edge.
    """
    def __init__(self, u, v, force, **kwargs):
        attrs = {"force": force, "type": "deviation"}
        super(DeviationEdge, self).__init__(u, v, attrs, **kwargs)

    def __repr__(self):
        """
        """
        force = self.attributes["force"]
        msg = "{name}(force={force!r}, state={state!r})"
        info = {"name": self.__class__.__name__,
                "force": fabs(force),
                "state": int(copysign(1, force))}

        return msg.format(**info)

# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
