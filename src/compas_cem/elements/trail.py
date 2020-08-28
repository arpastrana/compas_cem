from compas.geometry import Line


class TrailEdge(Line):
    """
    A trail edge.
    """

    def __init__(self, *args, **kwargs):
        super(TrailElement, self).__init__(*args, **kwargs)


if __name__ == "__main__":
    pass
