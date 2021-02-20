from compas.geometry import distance_point_point

from compas_cem.optimization.goals import Goal


__all__ = [
    "DeviationEdgeLengthGoal"
]


class DeviationEdgeLengthGoal(Goal):
    """
    Make a deviation edge reach a target length.
    """
    def __init__(self, edge=None, length=None):
        # TODO: needs different serialization mechanism
        super(DeviationEdgeLengthGoal, self).__init__(edge, length)

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

        return diff * diff

    def reference(self, data):
        """
        """
        u, v = self.key()
        point_a = data["node_xyz"][u]
        point_b = data["node_xyz"][v]

        return distance_point_point(point_a, point_b)


if __name__ == "__main__":
    pass
