from compas_cem.diagrams import Diagram


__all__ = [
    "FormDiagram"
]

# ==============================================================================
# Form Diagram
# ==============================================================================

class FormDiagram(Diagram):
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
    form : ``FormDiagram``
        A form diagram.
    """

    def __init__(self, *args, **kwargs):
        super(FormDiagram, self).__init__(*args, **kwargs)
        
        self.update_default_node_attributes({
                                            "x": 0.0,
                                            "y": 0.0,
                                            "z": 0.0,
                                            "qx": 0.0,
                                            "qy": 0.0,
                                            "qz": 0.0,
                                            "rx": 0.0,
                                            "ry": 0.0,
                                            "rz": 0.0,
                                            "type": None,
                                            "_w": None
                                            })

        self.update_default_edge_attributes({
                                            "type": None,
                                            "length": 0.0,
                                            "force": 0.0
                                            })

        self.attributes["gkey_node"] = {}
        self.attributes["tol"] = "3f"

# ==============================================================================
# Properties
# ==============================================================================

    @property
    def tol(self):
        """
        """
        return self.attributes["tol"]
    
    @tol.setter
    def tol(self, tol):
        """
        """
        self.attributes["tol"] = tol

    @property
    def gkey_node(self):
        """
        """
        return self.attributes["gkey_node"]

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
        Collects the trails in the form diagram.

        A trail is an ordered sequence of nodes with two characteristics:
        there is a root node at the start, and a support node at the end.

        Returns
        -------
        trails : ``dict``
            The trails.
            Their keys in the dictionary correspond to the found root nodes.
        
        Note
        ----
            Root nodes are computed as part of the trail-making process.
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
                    root = node
                    trail.append(root)
                    visited.add(node)
                    break

            # set last node to be of root type
            self.node_attribute(root, "type", "root")

            trail.reverse()

            # assign topological distances
            # root should be _w= 0, support _w=len(trail)
            for index, node in enumerate(trail):
                self.node_attribute(node, "_w", index)

            tr[root] = trail
            nodes_in_trails.update(visited)

        # output sanity checks
        # all nodes must belong to a trail
        unassigned_nodes = set(self.nodes()) - nodes_in_trails
        msg = "Nodes {} haven't been assigned to a trail. Check your topology!"
        assert len(unassigned_nodes) == 0, msg

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
        # TODO: Attribute "root" might be better off as private "_root".
        # What if a user wants to artificially set a node as root. Now possible.
        # Either explicitely private or completely out of the public API.
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
# Edge Attributes
# ==============================================================================

    def edge_force(self, edge):
        """
        Gets the force value at an edge.

        Parameters
        ----------
        edge : ``tuple``
            The u, v edge key.

        Return
        ------
        force : ``float``
            The force value in the edge.
        """
        return self.edge_attribute(key=edge, name="force")


# ==============================================================================
# Node Attributes
# ==============================================================================

    def node_load(self, node):
        """
        Gets the load applied at a node.
        
        Parameters
        ----------
        node : ``int``
            A node key.
        load : ``list``
            A vector with xyz components.
            If load is ``None``, this function queries the load vector at the
            node.
            Otherwise, it assigns it. Defaults to ``None``.
        
        Returns
        -------
        load_vector: ``list``
            A vector with xyz components if ``load`` is ``None``.
        """
        return self.node_attributes(key=node, names=["qx", "qy", "qz"])

    def node_residual(self, node):
        """
        Gets the residual force vector at a node.
        
        Parameters
        ----------
        node : ``int``
            A node key.
        
        Returns
        -------
        type : ``list``
            The residual force vector.
        """
        return self.node_attributes(key=node, names=["rx", "ry", "rz"])


# ==============================================================================
# Node Filters
# ==============================================================================

    def is_node_root(self, node):
        """
        Checks if a node is a root node.

        Parameters
        ----------
        node : ``int``
            A node key.
        
        Returns
        -------
        flag : ``bool``
            ``True``if the node is a root node. ``False`` otherwise.
        """
        return self.node_attribute(key=node, name="type") == "root"
    
    def is_node_support(self, node):
        """
        Checks if a node is a support.

        Parameters
        ----------
        node : ``int``
            A node key.
        
        Returns
        -------
        flag : ``bool``
            ``True``if the node is a support. ``False`` otherwise.
        """
        return self.node_attribute(key=node, name="type") == "support"


# ==============================================================================
# Edge Filters
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
            a, b = self._edge_topological_distance(edge)
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
            a, b = self._edge_topological_distance(edge)
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


    def _node_topological_distance(self, node):
        """
        Gets the distance of a node to the root node of the trail it belongs to.

        Parameters
        ----------
        node : ``int``
            The node key.

        Returns
        -------
        w : ``int``
            The number of nodes between the current node and the root node.
        """
        w = self.node_attribute(key=node, name="_w")

        if w is None:
            msg = "Topological distance at node {} is None. Try running FormDiagram.trails() first."
            raise ValueError(msg.format(node))

        return w

    def _edge_topological_distance(self, edge):
        """
        Gets the distance of the nodes of an edge to the root nodes of the trails they belongs to.

        Parameters
        ----------
        edge : ``tuple`
            The edge key.

        Returns
        -------
        w_edge : ``tuple``
            The number of nodes between the edge's nodes and their corresponding root nodes.
        """

        return  tuple([self._node_topological_distance(node) for node in edge])

# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    form = FormDiagram()
    form.edges_where_predicate()
    print(form)
