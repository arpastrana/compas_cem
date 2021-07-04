from compas.geometry import distance_point_point

from compas_cem.optimization.constraints import Constraint


__all__ = ["DeviationEdgeLengthConstraint"]


class DeviationEdgeLengthConstraint(Constraint):
    """
    Make a deviation edge reach a target length.
    """
    def __init__(self, edge=None, length=None, weight=1.0):
        # TODO: needs different serialization mechanism
        super(DeviationEdgeLengthConstraint, self).__init__(edge, length, weight)

    def error(self, data):
        """
        The length error of a deviation edge.

        Returns
        -------
        error : ``float``
            The squared difference bewteen the current and the target length.
        """
        length_a = self.reference(data)
        length_b = self.target()

        diff = length_a - length_b

        return diff * diff * self.weight

    def reference(self, data):
        """
        """
        u, v = self.key()
        point_a = data["node_xyz"][u]
        point_b = data["node_xyz"][v]

        return distance_point_point(point_a, point_b)


if __name__ == "__main__":
    pass
