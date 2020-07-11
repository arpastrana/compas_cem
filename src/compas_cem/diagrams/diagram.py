from compas.datastructures import Network


class Diagram(Network):
    """
    Base class that shares functionality across diagrams.
    """

    def __init__(self, *args, **kwargs):
        super(Diagram, self).__init__(*args, **kwargs)