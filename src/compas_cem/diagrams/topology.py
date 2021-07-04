from compas_cem.diagrams import Diagram


__all__ = ["TopologyDiagram"]

# ==============================================================================
# Form Diagram
# ==============================================================================


class TopologyDiagram(Diagram):
    """
    The very heart of life.

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

        self.attributes["trails"] = {}

# ==============================================================================
# Node Additions
# ==============================================================================

    def add_support(self, support):
        """
        Adds a support.

        Parameters
        ----------
        support : ``NodeSupport``
            A node support object.

        Notes
        -----
        Support nodes mark the end of a continuous trail. They aren't fixed.
        """
        value = support.node
        if value is None:
            value = support.xyz
        node = self.node_key(value)

        if node is None:
            raise ValueError("A node doesn't exist at {} yet!".format(value))

        self.node_attribute(node, "type", "support")

    def add_load(self, load):
        """
        Applies a load.

        Parameters
        ----------
        load : ``Load``
            A load object.
        """
        value = load.node
        if value is None:
            value = load.xyz
        node = self.node_key(value)
        if node is None:
            raise ValueError("A node doesn't exist at {} yet!".format(value))

        self.node_attributes(node, ["qx", "qy", "qz"], load.vector)

# ==============================================================================
# Trails
# ==============================================================================

    def trails(self):
        """
        The trails in the topology diagram.

        Returns
        -------
        trails : ``dict``
            A dictionary with trails.
            Every trail is stored with its origin node as key.
        """
        return self.attributes["trails"]

    def number_of_trails(self):
        """
        Number of trails in the topology diagram.

        Return
        ------
        number : ``int``
            The number of trails.
        """
        return len(self.trails())

    def build_trails(self):
        """
        Automatically builds the trails in the topology diagram.

        A trail is an ordered sequence of nodes with two characteristics:
        there is a root node at the start, and a support node at the end.

        Returns
        -------
        trails : ``dict``
            The trails.
            Their keys in the dictionary correspond to the found origin nodes.

        Notes
        -----
            Origin nodes are computed as part of the trail-making process.
        """
        tr = {}

        # input sanity checks
        # there must be at least one trail edge
        assert len(list(self.trail_edges())) > 0, "No trail edges defined!"
        # there must be at least one support node for trails to run
        assert len(list(self.support_nodes())) > 0, "No supports assigned!"

        # trail search
        nodes_in_trails = set()

        for support in self.support_nodes():

            trail = []
            visited = set()
            node = support

            while True:

                last_node = node
                neighbors = self.neighbors(node)

                while neighbors:
                    neighbor = neighbors.pop()

                    if neighbor in visited:
                        continue

                    try:
                        is_trail = self.is_trail_edge((node, neighbor))
                    except KeyError:
                        is_trail = self.is_trail_edge((neighbor, node))

                    if not is_trail:
                        continue

                    trail.append(node)
                    visited.add(node)
                    node = neighbor
                    break

                if last_node == node:
                    origin = node
                    trail.append(origin)
                    visited.add(node)
                    break

            # set last node to be origin/start node
            self.node_attribute(origin, "type", "_origin")

            trail.reverse()

            # assign node sequences
            # start should be _k= 0, support _k=len(trail)
            for index, node in enumerate(trail):
                self.node_attribute(node, "_k", index)

            tr[origin] = trail
            nodes_in_trails.update(visited)

        # output sanity checks
        # all nodes must belong to a trail
        unassigned_nodes = set(self.nodes()) - nodes_in_trails
        msg = "Nodes {} haven't been assigned to a trail. Check your topology!"
        assert len(unassigned_nodes) == 0, msg

        # store trails in topology diagram
        self.attributes["trails"] = tr

        return tr

# ==============================================================================
#  Node Collections
# ==============================================================================

    def origin_nodes(self):
        """
        Starting nodes of all trails.

        Yields
        -------
        origin_node : ``int``
            The key of the next origin node.
        """
        return self.nodes_where({"type": "_origin"})

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
        Direct deviation edges have both end-nodes with equal topological
        distance to a root node. Distances must be precomputed.
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
        Indirect deviation edges have both end-nodes with unequal topological
        distance to a root node. Distances must be precomputed.
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
# Node Filters
# ==============================================================================

    def is_node_origin(self, node):
        """
        Checks if a node is an origin node.

        Parameters
        ----------
        node : ``int``
            A node key.

        Returns
        -------
        flag : ``bool``
            ``True``if the node is a origin node.
            ``False`` otherwise.
        """
        return self.node_attribute(key=node, name="type") == "_origin"

# ==============================================================================
# Edge Predicates
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
            a, b = self.edge_sequence(edge)
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
            a, b = self.edge_sequence(edge)
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
        Similar to ``FormDiagram.edges_where_predicate()``.
        """
        if not self.is_deviation_edge(edge):
            return False
        if predicate(edge):
            return True
        return False

# ==============================================================================
#  Sequences
# ==============================================================================

    def node_sequence(self, node):
        """
        Gets the sequence a node is assigned to.

        Parameters
        ----------
        node : ``int``
            The node key.

        Returns
        -------
        k : ``int``
            The sequence key.
        """
        k = self.node_attribute(key=node, name="_k")
        if k is None:
            msg = "Node {} is unassigned. Try building trails first."
            raise ValueError(msg.format(node))

        return k

    def edge_sequence(self, edge):
        """
        Gets the sequence of the nodes of a given edge.

        Parameters
        ----------
        edge : ``tuple``
            The edge key.

        Returns
        -------
        sequences : ``tuple``
            The nodes sequences.
        """
        u, v = edge
        return self.node_sequence(u), self.node_sequence(v)

    def sequences(self):
        """
        Iterate over the sequences in the diagram.

        Yields
        ------
        sequence : `int`
            The next sequence number.
        """
        return range(self.sequence_max())

    def sequence_max(self):
        """
        The largest sequence number.

        Yields
        ------
        sequence : `int`
            The largest sequence number.
        """
        return max([len(trail) for trail in self.trails().values()])

# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
