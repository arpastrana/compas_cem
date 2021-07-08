from compas_cem.elements import Edge


class DeviationEdge(Edge):
    """
    A deviation edge.
    """
    def __init__(self, u, v, force):
        super(DeviationEdge, self).__init__(u, v)
        self.attributes = {"force": force, "type": "deviation"}

    def __repr__(self):
        """
        """
        return "{}(force={})".format(self.__class__.__name__, self.attributes["force"])


if __name__ == "__main__":
    pass
