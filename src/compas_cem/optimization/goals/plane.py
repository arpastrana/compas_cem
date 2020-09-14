from compas.geometry import closest_point_on_plane
from compas.geometry import distance_point_point_sqrd

from compas_cem.optimization.goals import Goal


__all__ = [
    "PlaneGoal"
]


class PlaneGoal(Goal):
    def __init__(self, node=None, plane=None):
        super(PlaneGoal, self).__init__(node, plane)
        self.target_point = None

    def target_geometry(self):
        """
        """
        return self._target_point

    def update(self, form):
        """
        """
        self._ref_geo = form.node_xyz(self.key())
        plane = self._target_geo
        self._target_point = closest_point_on_plane(self._ref_geo, plane)

    def error(self):
        """
        """
        a = self.target_geometry()
        b = self.reference_geometry()
        return distance_point_point_sqrd(a, b)

if __name__ == "__main__":
    pass
