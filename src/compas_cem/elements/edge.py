from compas_rhino.geometry import RhinoLine


class Edge(object):
    """
    The edge base class.
    """
    def __init__(self, u, v):
        self.u = u
        self.v = v

    @classmethod
    def from_line(cls, line, *args, **kwargs):
        """
        """
        return cls(line.start, line.end, *args, **kwargs)
    
    @classmethod
    def from_rhinoline(cls, rhino_line, *args, **kwargs):
        """
        """
        line = RhinoLine.from_geometry(rhino_line).to_compas()
        return cls.from_line(line, *args, **kwargs)

if __name__ == "__main__":
    pass


