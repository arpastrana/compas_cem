from compas_cem.optimization.goal import VectorGoal

__all__ = ["TrimeshGoal"]


class TrimeshGoal(VectorGoal):
    """
    Pulls the xyz position of a node to a target triangular mesh.

    TODO: trimesh complaints with autograd boxes when parsing into array.
    """

    def __init__(self, node=None, trimesh=None, weight=1.0):
        super(TrimeshGoal, self).__init__(node, trimesh, weight)

    def reference(self, data):
        """ """
        return data["node_xyz"][self.key()]

    def target(self, ref):
        """ """
        points = [ref]
        trimesh = self._target
        closest, dist, _ = trimesh.nearest.on_surface(points)

        return closest.tolist().pop()


if __name__ == "__main__":
    pass
