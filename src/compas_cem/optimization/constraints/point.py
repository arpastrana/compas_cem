from compas_cem.optimization.constraints import VectorConstraint


__all__ = ["PointConstraint"]


class PointConstraint(VectorConstraint):
    """
    Pulls the xyz position of a node to a target point.
    """
    def __init__(self, node=None, point=None, weight=1.0):
        super(PointConstraint, self).__init__(key=node, target=point, weight=weight)

    def reference(self, data):
        """
        Gets the reference to compare the target against.
        """
        return data["node_xyz"][self.key()]


if __name__ == "__main__":
    pass
