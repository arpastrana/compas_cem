from compas_cem.optimization.goals import Goal

from compas.geometry import distance_point_point_sqrd


__all__ = [
    "PointGoal",
]
    

class PointGoal(Goal):
    def __init__(self, node=None, point=None):
        super(PointGoal, self).__init__(node, point)

    def update(self, topology):
        """
        """
        self._ref_geo = topology.node_coordinates(self.key())

    def error(self):
        """
        """
        a = self.target_geometry()
        b = self.reference_geometry()
        return distance_point_point_sqrd(a, b)


if __name__ == "__main__":
    pass
