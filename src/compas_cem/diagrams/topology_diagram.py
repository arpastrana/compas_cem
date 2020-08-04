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
                                            "state": None,  # 1, -1
                                            "length": 0.0,  # only positive
                                            "force": 0.0,  # only positive
                                            })

# ==============================================================================
# Node Additions
# ==============================================================================

    def support(self, node):
        """
        Sets a node to a support node.
        
        Parameters
        ----------
        node : ``int``
            A node key.
        """
        self.node_attribute(node, "type", "support")

    def root(self, node):
        """
        Sets a node to a root node.

        Parameters
        ----------
        node : ``int``
            A node key.
        position : ``list``
            The node xyz coordinates.
        """
        self.node_attribute(node, "type", "root")

    def add_load(self, node, load):
        """
        Parameters
        ----------
        node : ``int``
            A node key.
        load : ``list``
            A load xyz vector.
        """
        for q, attr in zip(load, ["qx", "qy", "qz"]):
            self.node_attribute(node, attr, q)
    
    def add_node_from_xyz(self, node, xyz):
        """
        Adds a node from xyz coordinates.

        Parameters
        ----------
        node : ``int``
            A node key.
        xyx : ``list``
            The node xyz coordinates.
        
        Returns
        -------
        node : ``int``
            The node key.
        """
        x, y, z = xyz
        return self.add_node(key=node, x=x, y=y, z=z)

# ==============================================================================
# Edge Additions
# ==============================================================================

    def add_trail_edge(self, edge, state, length):
        """
        Adds a trail edge.

        Parameters
        ----------
        edge : ``tuple``
            An edge key.
        state : ``int``
            A combinatorial state. ``1`` if tension. ``-1`` if compression.
        length : ``float``
            The length of the edge.

        Returns
        -------
        edge : ``tuple``
            The edge key.
        """
        u, v = edge
        kwargs = {"type": "trail", "state": state, "length": length}
        return self.add_edge(u, v, **kwargs)

    def add_deviation_edge(self, edge, state, force):
        """
        Adds a deviation edge.

        Parameters
        ----------
        edge : ``tuple``
            An edge key.
        state : ``int``
            A combinatorial state. ``1`` if tension. ``-1`` if compression.
        force : ``float``
            The force assigned to the edge.

        Returns
        -------
        edge : ``tuple``
            The edge key.
        """
        u, v = edge
        kwargs = {"type": "deviation", "state": state, "force": force}
        return self.add_edge(u, v, **kwargs)

# ==============================================================================
# Trails
# ==============================================================================

    def trails(self):
        """
        Collects the trails in the topology diagram.

        A trail is an ordered sequence of nodes with two characteristics:
        there is a root node at the start, and a support node at the end

        Returns
        -------
        trails : ``dict``
            The trails. Keys are those of their root nodes
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
#  Node Queries
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

    def connected_deviation_edges(self, node):
        """
        Parameters
        ----------
        node : ``int``
            A node key.
        
        Returns
        -------
        deviation_edges : ``list``
            A list with the keys of the deviation edges connected to the node.
            If no deviation edge is attached, the list will be empty.
        """
        deviation_edges = []
        for edge in self.connected_edges(node):
            if self.edge_attribute(edge, "type") == "deviation":
                deviation_edges.append(edge)
        return deviation_edges

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