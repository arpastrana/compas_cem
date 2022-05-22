from compas.geometry import distance_point_point

from compas_cem.optimization.constraints import FloatConstraint


__all__ = ["DeviationEdgeLengthConstraint"]


class DeviationEdgeLengthConstraint(FloatConstraint):
    """
    Make a deviation edge reach a target length.
    """
    def __init__(self, edge=None, length=None, weight=1.0):
        super(DeviationEdgeLengthConstraint, self).__init__(edge, length, weight)

    def reference(self, data):
        """
        """
        u, v = self.key()
        point_a = data["node_xyz"][u]
        point_b = data["node_xyz"][v]

        try:
            length = distance_point_point(point_a, point_b)
        except TypeError:
            # TODO: This import should not happen here
            import autograd.numpy as np
            length = np.linalg.norm(point_a - point_b)

        return length


if __name__ == "__main__":
    pass
