from compas_cem.elements import Edge


class TrailEdge(Edge):
    """
    A trail edge.
    """
    def __init__(self, u, v, length):
        super(TrailEdge, self).__init__(u, v)
        self.attributes = {"length": length, "type": "trail"}

    def __repr__(self):
        """
        """
        return "{}(length={})".format(self.__class__.__name__, self.attributes["length"])


if __name__ == "__main__":
    pass
