from compas_cem.optimization.goals import Goal


__all__ = [
    "DeviationEdgeLengthGoal"
]


class DeviationEdgeLengthGoal(Goal):
    def __init__(self, edge=None, length=None):
        # TODO: needs different serialization mechanism
        super(DeviationEdgeLengthGoal, self).__init__(edge, length)

    def target_geometry(self):
        """
        """
        return self._target_geo

    def update(self, form):
        """
        """
        u, v = self.key()
        self._ref_geo = form.edge_length(u, v)
        
    def error(self):
        """
        """
        diff = self.reference_geometry() - self.target_geometry()
        return diff * diff


if __name__ == "__main__":
    pass
