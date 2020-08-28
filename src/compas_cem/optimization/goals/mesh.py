import numpy as np

from trimesh import Trimesh
from trimesh.proximity import closest_point

from compas_cem.optimization.goals import Goal


__all__ = [
    "MeshGoal",
]


class MeshGoal(Goal):
    def __init__(self, node, mesh):
        vertices, faces = mesh.to_vertices_and_faces()
        trimesh = Trimesh(vertices, faces)
        super(MeshGoal, self).__init__(node, trimesh)
        self.target_point = None

    def target_geometry(self):
        """
        """
        return self._target_point

    def update(self, topology):
        """
        """
        self._ref_geo = topology.node_coordinates(self.key())
        trimesh = self._target_geo
        point = np.array(self._ref_geo).reshape((1, 3))
        closest, distance, _ = closest_point(trimesh, point)
        self._target_point = closest.tolist().pop()

if __name__ == "__main__":
    pass
