from compas_rhino.geometry import RhinoPoint


class Node(object):
    """
    The node base class.
    """
    def __init__(self, key=None, xyz=None):
        self.key = key
        self.xyz = xyz
        self.attributes = {}

    @classmethod
    def from_point(cls, point):
        """
        """
        return cls(xyz=point)
    
    @classmethod
    def from_rhino_point(cls, rhino_point):
        """
        """
        point = RhinoPoint.from_geometry(rhino_point).to_compas()
        return cls.from_point(point)

    def __repr__(self):
        """
        """
        return "{}(key={}, xyz={})".format(self.__class__.__name__, self.key, self.xyz)

if __name__ == "__main__":
    pass


