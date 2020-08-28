from compas_cem.optimization.goals import Goal


__all__ = [
    "PointGoal",
]
    

class PointGoal(Goal):
    def __init__(self, node, point):
        super(PointGoal, self).__init__(node, point)

    def update(self, topology):
        """
        """
        self._ref_geo = topology.node_coordinates(self.key())


if __name__ == "__main__":
    pass
