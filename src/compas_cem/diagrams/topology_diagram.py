from compas_cem.diagrams import Diagram


__all__ = [
    "TopologyDiagram"
]

# ==============================================================================
# Topology Diagram
# ==============================================================================

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
# Node Attributes
# ==============================================================================

    def support(self, node):
        """
        Assigns a support attribute to a node.
        
        Parameters
        ----------
        node : ``int``
            A node key.
        """
        self.node_attribute(node, "type", "support")

    def root(self, node):
        """
        Marks a node as the starting point of a continuous trail.

        Parameters
        ----------
        node : ``int``
            A node key.
        position : ``list``
            The node xyz coordinates.
        """
        self.node_attribute(node, "type", "root")

    def node_load(self, node, load=None):
        """
        Gets or sets a load at a node.
        
        Parameters
        ----------
        node : ``int``
            A node key.
        load : ``list``
            A vector with xyz components.
            If load is ``None``, this function queries the load vector at the
            node.
            Otherwise, it assigns it.
            Defaults to ``None``.
        
        Returns
        -------
        load_vector: ``list``
            A vector with xyz components, if ``load`` is ``None``.
        """
        attrs = ["qx", "qy", "qz"]
        return self.node_attributes(key=node, names=attrs, values=load)

# ==============================================================================
# Node Additions
# ==============================================================================

    def add_load(self, node, load):
        """
        Adds a nodal load.

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

# ==============================================================================
#  Connected Edges
# ==============================================================================

    def connected_deviation_edges(self, node):
        """
        Finds the deviation edges connected to a node.

        Parameters
        ----------
        node : ``int``
            A node key.
        
        Returns
        -------
        deviation_edges : ``list``
            The keys of the connected deviation edges.
            If no deviation edge is attached, the list will be empty.
        """
        return self._connected_edges_predicate(node, self.is_deviation_edge)

    def connected_trail_edges(self, node):
        """
        Finds the trail edges connected to a node.

        Parameters
        ----------
        node : ``int``
            A node key.
        
        Returns
        -------
        trail_edges : ``list``
            The keys of the connected trail edges.
            If no trail edge is attached, the list will be empty.
        """
        return self._connected_edges_predicate(node, self.is_trail_edge)

    def _connected_direct_deviation_edges(self, node):
        """
        Finds the direct deviation edges connected to a node.

        Parameters
        ----------
        node : ``int``
            A node key.
        
        Returns
        -------
        deviation_edges : ``list``
            The keys of the connected deviation edges.
            If no deviation edge is attached, the list will be empty.

        Note
        ----
            Direct deviation edges have both end-nodes with equal topological distance to a root node. Distances must be precomputed.
        """
        return self._connected_edges_predicate(node, self._is_direct_deviation_edge)

    def _connected_indirect_deviation_edges(self, node):
        """
        Finds the indirect deviation edges connected to a node.

        Parameters
        ----------
        node : ``int``
            A node key.
        
        Returns
        -------
        deviation_edges : ``list``
            The keys of the connected deviation edges.
            If no deviation edge is attached, the list will be empty.

        Note
        ----
            Indirect deviation edges have both end-nodes with unequal topological distance to a root node. Distances must be precomputed.
        """
        return self._connected_edges_predicate(node, self._is_indirect_deviation_edge)

    def _connected_edges_predicate(self, node, predicate):
        """
        Finds the edges connected to a node.

        Parameters
        ----------
        node : ``int``
            A node key.
        predicate : ``func``
            A predicate function to search for a specific edge type.
        
        Returns
        -------
        selected_edges : ``list``
            The keys of the selected edges.
            If no edge of the given type is attached, the list will be empty.
        """
        deviation_edges = []
        for edge in self.connected_edges(node):
            if predicate(edge):
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

# ==============================================================================
# Edge Selections
# ==============================================================================

    def is_trail_edge(self, edge):
        """
        Tests whether or not an edge is a trail edge.

        Parameters
        ----------
        edge : ``tuple``
            The key of the edge to test.
        
        Returns
        -------
        flag : ``bool``
            ``True``if the edge is a trail edge. ``False`` otherwise.
        """
        if self.edge_attribute(edge, "type") == "trail":
            return True
        return False

    def is_deviation_edge(self, edge):
        """
        Tests whether or not an edge is a deviation edge.

        Parameters
        ----------
        edge : ``tuple``
            The key of the edge to test.
        
        Returns
        -------
        flag : ``bool``
            ``True``if the edge is a deviation edge. ``False`` otherwise.
        """
        if self.edge_attribute(edge, "type") == "deviation":
            return True
        return False

    def _is_direct_deviation_edge(self, edge):
        """
        Tests if a deviation edge is direct.

        Parameters
        ----------
        edge : ``tuple``
            The key of the edge to test.
        
        Returns
        -------
        flag : ``bool``
            ``True``if the deviation edge is direct.
            ``False`` otherwise.
        """
        def predicate(x):
            a, b = self.nodes_attribute(name="_w", keys=edge)
            if a == b:
                return True

        return self._is_deviation_edge_predicate(edge, predicate)

    def _is_indirect_deviation_edge(self, edge):
        """
        Tests if a deviation edge is indirect.
        
        Parameters
        ----------
        edge : ``tuple``
            The key of the edge to test.
        
        Returns
        -------
        flag : ``bool``
            ``True``if the deviation edge is indirect.
            ``False`` otherwise.
        """
        def predicate(x):
            a, b = self.nodes_attribute(name="_w", keys=edge)
            if a != b:
                return True

        return self._is_deviation_edge_predicate(edge, predicate)
    
    def _is_deviation_edge_predicate(self, edge, predicate):
        """
        Tests whether or not a deviation edge fulfills a set of conditions.

        Parameters
        ----------
        edge : ``tuple``
            The key of the edge to test.
        predicate : ``func``
            A function that for user-defined test conditions.
            Predicate must take in a single edge key as argument.
        
        Returns
        -------
        flag : ``bool``
            ``True``if the deviation edge meets the predicate condition.
            ``False`` otherwise.
        
        Notes
        -----
        Similar to ``TopologyDiagram.edges_where_predicate()``.
        """
        if not self.is_deviation_edge(edge):
            return False
        if predicate(edge):
            return True
        return False

# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    topology = TopologyDiagram()
    topology.edges_where_predicate()
    print(topology)
