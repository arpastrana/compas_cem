from compas_cem.optimization.constraint import Constraint

from compas.geometry import distance_point_point_sqrd

import numpy as np


__all__ = ["TrimeshConstraint"]


class TrimeshConstraint(Constraint):
    """
    Pulls the xyz position of a node to a target triangular mesh.

    TODO: trimesh complaints with autograd boxes when parsing into array.
    """
    def __init__(self, node=None, trimesh=None, weight=1.0):
        super(TrimeshConstraint, self).__init__(node, trimesh, weight)

    def error(self, data):
        """
        """
        point_a = self.reference(data)
        point_b = self.target(point_a)

        return distance_point_point_sqrd(point_a, point_b) * self.weight

    def reference(self, data):
        """
        """
        return data["node_xyz"][self.key()]

    def target(self, ref):
        """
        """
        points = np.array([ref])
        trimesh = self._target
        closest, dist, _ = trimesh.nearest.on_surface(points)

        return closest.tolist().pop()


if __name__ == "__main__":
    pass
