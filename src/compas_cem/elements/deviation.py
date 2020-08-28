from compas.geometry import Line


class DeviationElement(Line):
    """
    A deviation edge.
    """

    def __init__(self, *args, **kwargs):
        super(DeviationElement, self).__init__(*args, **kwargs)


if __name__ == "__main__":
    pass
