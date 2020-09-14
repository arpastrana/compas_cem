from compas_cem.elements import Edge


class DeviationEdge(Edge):
    """
    A deviation edge.
    """
    def __init__(self, u, v, force):
        super(DeviationEdge, self).__init__(u, v)
        self.attributes = {"force": force, "type": "deviation"}

if __name__ == "__main__":
    pass
