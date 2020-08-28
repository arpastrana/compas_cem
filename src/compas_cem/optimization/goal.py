from compas_cem.optimization import pull_point_to_plane
from compas_cem.optimization import pull_point_to_mesh


__all__ = [
    "PointGoal",
    "PlaneGoal"
]


class Goal(object):
    def __init__(self, key, target_geo):
        self._key = key  # a topological key
        self._target_geo = target_geo  # a geometric target
        self._ref_geo = None
    
    def key(self):
        return self._key
    
    def reference_geometry(self):
        """
        """
        return self._ref_geo
    
    def target_geometry(self):
        """
        """
        return self._target_geo
    
    def update(self):
        return
    
    def error(self):
        return
    

class PointGoal(Goal):
    def __init__(self, node, point):
        super(PointGoal, self).__init__(node, point)

    def update(self, topology):
        """
        """
        self._ref_geo = topology.node_coordinates(self.key())


class PlaneGoal(Goal):
    def __init__(self, node, plane):
        super(PlaneGoal, self).__init__(node, plane)
        self.target_point = None

    def target_geometry(self):
        """
        """
        return self._target_point

    def update(self, topology):
        """
        """
        self._ref_geo = topology.node_coordinates(self.key())
        plane = self._target_geo
        self._target_point = pull_point_to_plane(self._ref_geo, plane)


class MeshGoal(Goal):
    def __init__(self, node, plane):
        super(MeshGoal, self).__init__(node, plane)
        self.target_point = None

    def target_geometry(self):
        """
        """
        return self._target_point

    def update(self, topology):
        """
        """
        self._ref_geo = topology.node_coordinates(self.key())
        mesh = self._target_geo
        self._target_point = pull_point_to_mesh(self._ref_geo, mesh)

if __name__ == "__main__":
    pass
