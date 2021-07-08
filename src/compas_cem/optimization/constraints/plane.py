from compas.geometry import closest_point_on_plane

from compas_cem.optimization.constraints import VectorConstraint


__all__ = ["PlaneConstraint"]


class PlaneConstraint(VectorConstraint):
    """
    Pulls the xyz position of a node to a target plane.
    """
    def __init__(self, node=None, plane=None, weight=1.0):
        super(PlaneConstraint, self).__init__(node, plane, weight)

    def reference(self, data):
        """
        """
        return data["node_xyz"][self.key()]

    def target(self, point):
        """
        """
        plane = self._target
        return closest_point_on_plane(point, plane)


if __name__ == "__main__":
    pass
