from compas_cem.optimization.goals import Goal

from compas.geometry import distance_point_point_sqrd


__all__ = [
    "TrimeshGoal",
]


class TrimeshGoal(Goal):
    """
    Pulls the xyz position of a node to a target triangular mesh.
    """
    def __init__(self, node=None, trimesh=None):
        super(TrimeshGoal, self).__init__(node, trimesh)
        self.target_point = None

    def target_geometry(self):
        """
        """
        return self._target_point

    def update(self, form):
        """
        """
        self._ref_geo = form.node_xyz(self.key())
        trimesh = self._target_geo
        point = [self._ref_geo]
        
        closest, distance, _ = trimesh.nearest.on_surface(point)
        self._target_point = closest.tolist().pop()

    def error(self):
        """
        """
        a = self.target_geometry()
        b = self.reference_geometry()
        return distance_point_point_sqrd(a, b)


if __name__ == "__main__":
    pass
