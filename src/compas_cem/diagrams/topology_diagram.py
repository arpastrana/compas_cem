from compas_cem.diagrams import Diagram


class TopologyDiagram(Diagram):
    """
    The notion of a topology diagram. The heart of life.

    Parameters
    ----------
    *args : ``list``
        Arguments.
    **kwargs : ``dict``
        Keyword arguments.

    Returns
    -------
    topology : ``TopologyDiagram``
        A topology diagram.
    """

    def __init__(self, *args, **kwargs):
        super(TopologyDiagram, self).__init__(*args, **kwargs)

        self.name = None
        self.g_vertex = {}

        self.default_vertex_attributes.update({
                                                "x": 0.0,
                                                "y": 0.0,
                                                "z": 0.0,
                                                "qx": 0.0,
                                                "qy": 0.0,
                                                "qz": 0.0,
                                                "is_fixed": False
                                            })

        self.default_edge_attributes.update({
                                                "type": None,  # trail, devi
                                                "state": 1,  # 1, -1
                                                "length": 0.0,  # only positive
                                                "force": 0.0,  # only positive
                                            })

# ==============================================================================
# Additions
# ==============================================================================

    def add_support(self, load):
        """
        """
        return

    def add_point_load(self, load):
        """
        """
        return

    def add_trail_edge(self, edge):
        """
        """
        return

    def add_direct_deviation_edge(self, edge):
        """
        """
        return

    def add_indirect_deviation_edge(self, edge):
        """
        """
        return

# ==============================================================================
# Properties
# ==============================================================================

    @property
    def trails(self, data=False):
        """
        """
        return self.edges_where({"type": "trail"}, data)

    @property
    def direct_deviation_edges(self, data=False):
        """
        """
        return self.edges_where({"type": "direct_deviation"}, data)

    @property
    def indirect_deviation_edges(self, data=False):
        """
        """
        return self.edges_where({"type": "indirect_deviation"}, data)

    def vertex_sequences(self):
        """
        """
        return

if __name__ == "__main__":
    topology = TopologyDiagram()
    print(topology)