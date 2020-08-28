from compas.geometry import closest_point_on_plane

from compas_cem.optimization.goals import Goal


__all__ = [
    "PlaneGoal"
]


class PlaneGoal(Goal):
    def __init__(self, node, plane):
        super(PlaneGoal, self).__init__(node, plane)
        self.target_point = None

    def target_geometry(self):
        """
        """
        return self._target_point

    def update(self, topology):
        """
        """
        self._ref_geo = topology.node_coordinates(self.key())
        plane = self._target_geo
        self._target_point = closest_point_on_plane(self._ref_geo, plane)


if __name__ == "__main__":
    pass
