from compas_cem.elements import Edge


class TrailEdge(Edge):
    """
    A trail edge.
    """
    def __init__(self, u, v, length):
        super(TrailEdge, self).__init__(u, v)
        self.length = length
    
    def __repr__(self):
        """
        """
        return "{}(length={})".format(self.__class__.__name__, self.length)


if __name__ == "__main__":
    pass
