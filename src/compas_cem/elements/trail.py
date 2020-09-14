from compas_cem.elements import Edge


class TrailEdge(Edge):
    """
    A trail edge.
    """
    def __init__(self, u, v, length):
        super(TrailEdge, self).__init__(u, v)
        self.attributes = {"length": length, "type": "trail"}

if __name__ == "__main__":
    pass
