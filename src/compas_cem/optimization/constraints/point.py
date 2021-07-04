from compas_cem.optimization.constraints import Constraint

from compas.geometry import distance_point_point_sqrd


__all__ = ["PointConstraint"]


class PointConstraint(Constraint):
    """
    Pulls the xyz position of a node to a target point.
    """
    def __init__(self, node=None, point=None, weight=1.0):
        super(PointConstraint, self).__init__(node, point, weight)

    def error(self, data):
        """
        The error between the xyz coordinates of a node and a target point.

        Returns
        -------
        error : ``float``
            The squared distance between two points.
        """
        a = self.reference(data)
        b = self.target()

        return distance_point_point_sqrd(a, b) * self.weight

    def reference(self, data):
        """
        Gets the reference to compare the target against.
        """
        a = data["node_xyz"][self.key()]
        return a


if __name__ == "__main__":
    pass
