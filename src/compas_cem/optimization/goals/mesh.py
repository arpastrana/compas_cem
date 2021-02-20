from compas_cem.optimization.goals import Goal

from compas.geometry import distance_point_point_sqrd

import numpy as np


__all__ = ["TrimeshGoal"]


class TrimeshGoal(Goal):
    """
    Pulls the xyz position of a node to a target triangular mesh.
    """
    def __init__(self, node=None, trimesh=None):
        super(TrimeshGoal, self).__init__(key=node, target=trimesh)

    def error(self, data):
        """
        """
        point_a = self.reference(data)
        point_b = self.target(point_a)

        return distance_point_point_sqrd(point_a, point_b)

    def reference(self, data):
        """
        """
        a = data["node_xyz"][self.key()]

        return a

    def target(self, ref):
        """
        """
        trimesh = self._target
        points = np.array([ref])
        closest, dist, _ = trimesh.nearest.on_surface(points)

        return closest.tolist().pop()


if __name__ == "__main__":
    pass
