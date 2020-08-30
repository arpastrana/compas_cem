from compas.geometry import closest_point_on_plane

from compas_cem.optimization.goals import Goal


__all__ = [
    "DeviationEdgeLengthGoal"
]


class DeviationEdgeLengthGoal(Goal):
    def __init__(self, node, length):
        super(DeviationEdgeLengthGoal, self).__init__(node, length)

    def target_geometry(self):
        """
        """
        return self._target_geo

    def update(self, topology):
        """
        """
        u, v = self.key()
        self._ref_geo = topology.edge_length(u, v)
        
        diff = self.reference_geometry() - self.target_geometry()
        return diff * diff


if __name__ == "__main__":
    pass
