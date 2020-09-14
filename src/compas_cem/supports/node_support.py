from compas_rhino.geometry import RhinoPoint


__all__ = [
    "NodeSupport"
]

# ==============================================================================
# Node Support
# ==============================================================================

class NodeSupport(object):
    """
    A support applied to a node.

    Parameters
    ----------
    node : ``int``
        The key of the node where to apply the support to.

    Returns
    -------
    node_support : ``PointSupport``
        A point support.
    """
    def __init__(self, node):
        self.node = node
        self.xyz = None
    
    @classmethod
    def from_point(cls, point):
        """
        """
        support = cls(node=None)
        support.xyz = point
        return support

    @classmethod
    def from_rhino_point(cls, rhino_point):
       """
       """
       xyz = RhinoPoint.from_geometry(rhino_point).to_compas()
       return cls.from_point(xyz)

if __name__ == "__main__":
    support = PointSupport([1.0, 0.0, 0,0])
    print(support)