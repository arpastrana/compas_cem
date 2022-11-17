from compas.geometry import closest_point_on_polyline

from compas_cem.optimization.constraints import VectorConstraint


__all__ = ["PolylineConstraint"]


class PolylineConstraint(VectorConstraint):
    """
    Pulls the xyz position of a node to a target polyline.
    """
    def __init__(self, node=None, plane=None, weight=1.0):
        super(PolylineConstraint, self).__init__(node, plane, weight)

    def reference(self, data):
        """
        The current xyz coordinates of the node.
        """
        return data["node_xyz"][self.key()]

    def target(self, point):
        """
        The closest point on the target polyline.
        """
        polyline = self._target
        return closest_point_on_polyline(point, polyline)


if __name__ == "__main__":
    pass
