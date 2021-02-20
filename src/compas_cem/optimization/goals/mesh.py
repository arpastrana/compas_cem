from compas_cem.optimization.goals import Goal

from compas.geometry import distance_point_point_sqrd

import jax.numpy as np

__all__ = [
    "TrimeshGoal",
]


class TrimeshGoal(Goal):
    """
    Pulls the xyz position of a node to a target triangular mesh.
    """
    def __init__(self, node=None, trimesh=None):
        super(TrimeshGoal, self).__init__(key=node, target=trimesh)

    def error(self, data):
        """
        """
        a = self.reference(data)
        b = self.target(a)

        return distance_point_point_sqrd(a, b)

    def reference(self, data):
        """
        """
        a = data.node_xyz(self.key())

        return a

    def target(self, ref):
        """
        """
        trimesh = self._target
        points = [ref]
        closest, dist, _ = trimesh.nearest.on_surface(points)

        return closest.tolist().pop()


if __name__ == "__main__":
    pass
