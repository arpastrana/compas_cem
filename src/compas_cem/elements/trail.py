from compas_cem.elements import Edge


class TrailEdge(Edge):
    """
    A trail edge.

    Notes
    -----
    If a plane is defined, it will override the absolute length of the trail edge.
    However, the sign of the length (e.g. the combinatorial state) is preserved.

    TODO: addexplicit combinatorial state to the signature of the constructor.
    """
    def __init__(self, u, v, length, plane=None):
        super(TrailEdge, self).__init__(u, v)
        self.attributes = {"length": length, "type": "trail", "plane": plane}
        # TODO
        # self.attributes = {"length": length, "state": state, type": "trail", "plane": plane}

    def __repr__(self):
        """
        """
        st = "{}(length={}, plane={})"
        return st.format(self.__class__.__name__, self.attributes["length"], self.attributes["plane"])


if __name__ == "__main__":
    pass
