from compas_cem.optimization.goals import Goal

from compas.geometry import distance_point_point_sqrd


__all__ = [
    "PointGoal",
]
    

class PointGoal(Goal):
    """
    Pulls the xyz position of a node to a target point.
    """
    def __init__(self, node=None, point=None):
        super(PointGoal, self).__init__(node, point)

    def update(self, form):
        """
        """
        self._ref_geo = form.node_xyz(self.key())

    def error(self):
        """
        """
        a = self.target_geometry()
        b = self.reference_geometry()
        return distance_point_point_sqrd(a, b)


if __name__ == "__main__":
    pass
