from compas_cem.diagrams import Diagram


class TopologyDiagram(Diagram):
    """
    The heart of life.

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

        self.update_default_node_attributes({
                                            "x": 0.0,
                                            "y": 0.0,
                                            "z": 0.0,
                                            "qx": 0.0,
                                            "qy": 0.0,
                                            "qz": 0.0,
                                            "type": None
                                            })

        self.update_default_edge_attributes({
                                            "type": None,  # trail, devi
                                            "comb_state": 1,  # 1, -1
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
# Trails
# ==============================================================================

    def trails(self):
        """
        Collects the trails in the topology diagram.

        A trail is an ordered sequence of nodes with two characteristics:
        a root node at the start, and a support node at the end

        Returns
        -------
        trails : ``dict``
            The trails. Keys are those  root nodes
        """
        tr = {}

        for root in self.root_nodes():
            trail = []

            node = root

            while True:
                visited = set()
                
                for neighbor in self.neighbors(node):

                    if neighbor in visited:
                        continue
                    
                    try:
                        edge_type = self.edge_attribute((node, neighbor), "type")
                    except KeyError:
                        edge_type = self.edge_attribute((neighbor, node), "type")

                    if edge_type == "trail":
                        trail.append(node)
                        node = neighbor
                        break

                if self.node_attribute(node, "type") == "support":
                    trail.append(node)
                    break

            tr[root] = trail

        return tr

# ==============================================================================
#  Nodes
# ==============================================================================

    def root_nodes(self):
        """
        Starting nodes of all trails.

        Yields
        -------
        root_node : ``int``
            The key of the next root node.
        """
        return self.nodes_where({"type": "root"})


    def support_nodes(self):
        """
        Nodes whose position is fixed in space.
        Also the ending nodes of all trails.

        Yields
        -------
        support_node : ``int``
            The key of the next root node.
        """
        return self.nodes_where({"type": "support"})

# ==============================================================================
# Edges
# ==============================================================================

    def trail_edges(self, data=False):
        """
        Iterates over the keys of all trail edges.

        Parameters
        ----------
        data : ``bool``
            ``True`` if the edges attributes should be yielded simultaneously.
            Defaults to ``False``.

        Yields
        -------
        trail_edge : ``tuple``
            The key of the next trail edge.
        attributes : ``dict``
            The attributes of the next trail edge if ``data=True``.
        """
        return self.edges_where({"type": "trail"}, data)

    def deviation_edges(self, data=False):
        """
        Iterates over the keys of all deviation edges.

        Parameters
        ----------
        data : ``bool``
            ``True`` if the edges attributes should be yielded simultaneously.
            Defaults to ``False``.

        Yields
        -------
        deviation_edge : ``tuple``
            The key of the next trail edge.
        attributes : ``dict``
            The attributes of the next deviation edge if ``data=True``.
        """
        return self.edges_where({"type": "deviation"}, data)


if __name__ == "__main__":
    topology = TopologyDiagram()
    print(topology)