from compas_cem.optimization.goals import Goal


__all__ = [
    "TrimeshGoal",
]


class TrimeshGoal(Goal):
    def __init__(self, node, trimesh):
        super(TrimeshGoal, self).__init__(node, trimesh)
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
        point = [self._ref_geo]
        closest, distance, _ = trimesh.nearest.on_surface(point)
        self._target_point = closest.tolist().pop()

if __name__ == "__main__":
    pass
