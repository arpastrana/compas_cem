import heapq
from collections import Counter
from collections import defaultdict

from compas.geometry import add_vectors
from compas.geometry import normalize_vector
from compas.geometry import scale_vector

from compas_cem.diagrams import Diagram
from compas_cem.diagrams.topology import MeshMixins
from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.supports import NodeSupport

__all__ = ["TopologyDiagram"]

# ==============================================================================
# Topology Diagram
# ==============================================================================


class TopologyDiagram(Diagram, MeshMixins):
    """
    The input to the form-finding algorithm.

    A topology diagram carries the nodes, the trail and deviation edges, the
    loads and the supports that describe a structure, but not the geometry that
    puts it in equilibrium. Solving one yields a form diagram.

    Parameters
    ----------
    *args :
        Arguments forwarded to the base diagram.
    **kwargs :
        Keyword arguments forwarded to the base diagram.
    """

    def __init__(self, *args, **kwargs):
        super(TopologyDiagram, self).__init__(*args, **kwargs)

        self.attributes["_trails"] = dict()
        self.attributes["_auxiliary_trails"] = dict()
        self.attributes["_aux_length"] = -1.0
        self.attributes["_aux_vector"] = [1.0, 1.0, 1.0]

    # ==============================================================================
    # Serialization
    # ==============================================================================

    @classmethod
    def __from_data__(cls, data):
        """
        Construct a topology diagram from a data dictionary.

        Parameters
        ----------
        data :
            A data dictionary.

        Returns
        -------
        topology :
            A topology diagram.

        Notes
        -----
        The trail bookkeeping is keyed by origin node and stored among the
        diagram attributes, which are serialized verbatim. JSON allows only
        string dictionary keys, so those keys are converted back to integers
        here. Without this the trails survive a round trip but can no longer be
        looked up by node key.
        """
        topology = super(TopologyDiagram, cls).__from_data__(data)

        for name in ("_trails", "_auxiliary_trails"):
            trails = topology.attributes.get(name) or {}
            topology.attributes[name] = {
                int(key): tuple(value) for key, value in trails.items()
            }

        return topology

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def auxiliary_trail_length(self):
        """
        The default length used to automatically create an auxiliary trail edge.

        Returns
        -------
        length :
            The signed length of the auxiliary trail edge.
        """
        return self.attributes["_aux_length"]

    @auxiliary_trail_length.setter
    def auxiliary_trail_length(self, length):
        self.attributes["_aux_length"] = length

    @property
    def auxiliary_trail_vector(self):
        """
        The default direction used to automatically create an auxiliary trail edge.

        Returns
        -------
        vector :
            The direction the auxiliary trail edge extends in.
        """
        return self.attributes["_aux_vector"]

    @auxiliary_trail_vector.setter
    def auxiliary_trail_vector(self, vector):
        self.attributes["_aux_vector"] = vector

    # ==============================================================================
    # Node Additions
    # ==============================================================================

    def add_support(self, support):
        """
        Adds a support.

        Parameters
        ----------
        support :
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
        load :
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
    # Counters
    # ==============================================================================

    def number_of_trails(self):
        """
        The number of trails in the topology diagram.

        Returns
        -------
        number :
            The number of trails.
        """
        return len(list(self.trails()))

    def number_of_auxiliary_trails(self):
        """
        The number of auxiliary trails in the topology diagram.

        Returns
        -------
        number :
            The number of auxiliary trails.
        """
        return len(list(self.auxiliary_trails()))

    def number_of_trail_edges(self):
        """
        The number of trail edges in the topology diagram.

        Returns
        -------
        number :
            The number of trail edges.
        """
        return len(list(self.trail_edges()))

    def number_of_deviation_edges(self):
        """
        The number of deviation edges in the topology diagram.

        Returns
        -------
        number :
            The number of deviation edges.
        """
        return len(list(self.deviation_edges()))

    def number_of_direct_deviation_edges(self):
        """
        The number of direct deviation edges in the topology diagram.

        Returns
        -------
        number :
            The number of direct deviation edges.
        """
        return len(list(self.direct_deviation_edges()))

    def number_of_indirect_deviation_edges(self):
        """
        The number of direct deviation edges in the topology diagram.

        Returns
        -------
        number :
            The number of direct deviation edges.
        """
        return len(list(self.indirect_deviation_edges()))

    # ==============================================================================
    # Trails
    # ==============================================================================

    def trail(self, key):
        """
        Gets the keys of the nodes in a trail.

        The nodes are sorted such that the first node is an origin node and the
        last, a support node.

        Parameters
        ----------
        key :
            The trail key, which is equivalent to the key of its origin node.

        Returns
        -------
        trail :
            The sorted node keys.
        """
        return self.attributes["_trails"][key]

    def trails(self, keys=False):
        """
        Iterate over all the existing trails in the topology diagram.

        Parameters
        ----------
        keys :
            If `True`, yield the trail key alongside the trail.

        Yields
        ------
        trail :
            The next trail if `keys` is `False`.
            Otherwise, a tuple with the trail key and the keys of the nodes on the trail.

        Notes
        -----
        A trail is an ordered sequence of node keys.
        This iterator yields auxiliary trails too, if any.
        """
        trails = self.attributes["_trails"]
        if not keys:
            return trails.values()
        return trails.items()

    def auxiliary_trails(self, keys=False):
        """
        Iterate over all the available auxiliary trails in the topology diagram.

        Parameters
        ----------
        keys :
            If `True`, yield the trail key alongside the trail.

        Yields
        ------
        aux_trail :
            The next auxiliary trail if `keys` is `False`.
            Otherwise, a tuple with the trail key and the keys of the nodes on the auxiliary trail.

        Notes
        -----
        An auxiliary trail is a helper trail with two nodes.
        """
        aux_trails = self.attributes["_auxiliary_trails"]
        if not keys:
            return aux_trails.values()
        return aux_trails.items()

    def has_trails(self):
        """
        Check if the topology diagram has trails.

        Returns
        -------
        flag :
            `True` if the topology diagram has at least one trail.
            Otherwise, `False`
        """
        return self.number_of_trails() > 0

    def shift_trail(self, key, sequence):
        """
        Shift all the nodes in a trail to start at a given sequence.

        Parameters
        ----------
        key :
            The key of the origin node of the trail.
        sequence :
            The new starting sequence of the trail.

            For example, if the current sequence of the origin node is 1 and k=3,
            then, the starting sequence of this trail becomes 3.
        """
        assert self.is_node_origin(key), "That is not an origin node!"

        if not self.has_trails():
            msg = "The diagram has no trails! Run topology.build_trails() first"
            raise ValueError(msg)

        trail = self.attributes["_trails"][key]
        for idx, node in enumerate(trail):
            sequence_new = sequence + idx
            self.node_attribute(node, name="_k", value=sequence_new)

    def align_trails(self):
        """
        Shift every trail so that as many deviation edges as possible are direct.

        Notes
        -----
        A deviation edge between two trails is direct when their starting
        sequences differ by the gap between the positions of its nodes along
        them. Between every pair of linked trails, the gap most of their edges
        agree on wins, and the trails are placed pair by pair, the pairs with
        the most agreeing edges first. Every group of linked trails then shifts
        so that its earliest trail starts at sequence 0, which discards earlier
        shifts. When every gap can be met, no deviation edge stays indirect.
        Otherwise, the edges that disagree with a winning gap stay indirect, as
        does an edge between two nodes of the same trail.
        """
        if not self.has_trails():
            msg = "The diagram has no trails! Run topology.build_trails() first"
            raise ValueError(msg)

        trail_links = self._trail_links()
        trail_starts = {}

        for root, _ in self.trails(keys=True):
            if root in trail_starts:
                continue

            trail_starts[root] = 0
            group = [root]
            frontier = []
            for count, origin, gap in trail_links[root]:
                entry = (-count, origin, gap, root)
                heapq.heappush(frontier, entry)

            while frontier:
                _, origin, gap, parent = heapq.heappop(frontier)
                if origin in trail_starts:
                    continue
                trail_starts[origin] = trail_starts[parent] + gap
                group.append(origin)
                for count, neighbor, step in trail_links[origin]:
                    if neighbor not in trail_starts:
                        entry = (-count, neighbor, step, origin)
                        heapq.heappush(frontier, entry)

            group_starts = [trail_starts[origin] for origin in group]
            start_min = min(group_starts)
            for origin in group:
                self.shift_trail(origin, trail_starts[origin] - start_min)

    def _trail_links(self):
        """
        Map every trail to the trails its deviation edges reach, each with the
        number of edges that agree on the winning gap and the gap itself.
        """
        trail_positions = {}
        for origin, trail in self.trails(keys=True):
            for position, node in enumerate(trail):
                trail_positions[node] = (origin, position)

        gap_votes = defaultdict(Counter)
        for u, v in self.deviation_edges():
            origin_u, position_u = trail_positions[u]
            origin_v, position_v = trail_positions[v]
            if origin_u == origin_v:
                continue
            # Order every pair one way, so both edge directions vote together.
            if origin_u > origin_v:
                origin_u, origin_v = origin_v, origin_u
                position_u, position_v = position_v, position_u
            pair = (origin_u, origin_v)
            gap_votes[pair][position_u - position_v] += 1

        trail_links = defaultdict(list)
        for (origin_u, origin_v), votes in gap_votes.items():
            ((gap, count),) = votes.most_common(1)
            link_forward = (count, origin_v, gap)
            link_backward = (count, origin_u, -gap)
            trail_links[origin_u].append(link_forward)
            trail_links[origin_v].append(link_backward)

        return trail_links

    def build_trails(self, auxiliary_trails=False):
        """
        Automatically generate the trails in the topology diagram.

        The process starts a graph traversal that begins from the support nodes in the diagram.
        A trail is an ordered sequence of nodes with two characteristics:
        - An origin node is the first node in the trail
        - A support node is the last node in the trail

        Parameters
        ----------
        auxiliary_trails :
            A flag to automatically append auxiliary trails to trail-unassigned nodes.

        Notes
        -----
            Origin nodes are computed in automatic as part of the trail-making process.
            Previous trails and auxiliary trails are recalculated every time
            this function is called.
        """
        trails = {}

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
                    origin_node = node
                    trail.append(origin_node)
                    visited.add(node)
                    break

            # set last node to be origin/start node
            self.node_attribute(origin_node, "type", "_origin")

            trail.reverse()

            # assign node sequences
            # start should be _k= 0, support _k=len(trail)
            for index, node in enumerate(trail):
                self.node_attribute(node, "_k", index)

            trails[origin_node] = tuple(trail)
            nodes_in_trails.update(visited)

        # output sanity checks
        # all nodes must belong to a trail
        unassigned = set(self.nodes()) - nodes_in_trails

        # automatically create auxiliary trails
        if auxiliary_trails:
            aux_trails = dict()
            aux_dir = normalize_vector(self.auxiliary_trail_vector)

            for node in unassigned:
                aux_vector = scale_vector(aux_dir, self.auxiliary_trail_length)
                aux_xyz = add_vectors(self.node_coordinates(node), aux_vector)
                aux_node = self.add_node(Node(xyz=aux_xyz))

                self.add_support(NodeSupport(aux_node))
                edge = self.add_edge(
                    TrailEdge(node, aux_node, self.auxiliary_trail_length)
                )
                aux_trails[node] = edge

            self.attributes["_auxiliary_trails"] = aux_trails
            print(
                "Warning: {} auxiliary trails have been added to the topology diagram!".format(
                    len(aux_trails)
                )
            )

            return self.build_trails(auxiliary_trails=False)

        # sanity checks
        # there must be at least one trail edge
        assert len(list(self.trail_edges())) > 0, "No trail edges defined!"
        # there must be at least one support node for trails to run
        assert len(list(self.support_nodes())) > 0, "No supports assigned!"
        # no free nodes
        msg = "Nodes {} haven't been assigned to a trail. Check your topology!".format(
            unassigned
        )
        assert len(unassigned) == 0, msg

        # store trails in topology diagram
        self.attributes["_trails"] = trails

    # ==============================================================================
    #  Node Collections
    # ==============================================================================

    def origin_nodes(self):
        """
        Starting nodes of all trails.

        Yields
        -------
        origin_node :
            The key of the next origin node.
        """
        return self.nodes_where({"type": "_origin"})

    def auxiliary_support_nodes(self):
        """
        Support nodes that end the auxiliary trails.

        Yields
        ------
        support_node :
            The key of the next support node of an auxiliary trail.

        Notes
        -----
        The origin node of an auxiliary trail belongs to the structure, so it is
        not yielded.
        """
        for edge in self.auxiliary_trails():
            for node in edge:
                if self.is_node_support(node):
                    yield node

    # ==============================================================================
    #  Connected Edges
    # ==============================================================================

    def connected_deviation_edges(self, node):
        """
        Finds the deviation edges connected to a node.

        Parameters
        ----------
        node :
            A node key.

        Returns
        -------
        deviation_edges :
            The keys of the connected deviation edges.
            If no deviation edge is attached, the list will be empty.
        """
        return self._connected_edges_predicate(node, self.is_deviation_edge)

    def connected_trail_edges(self, node):
        """
        Finds the trail edges connected to a node.

        Parameters
        ----------
        node :
            A node key.

        Returns
        -------
        trail_edges :
            The keys of the connected trail edges.
            If no trail edge is attached, the list will be empty.
        """
        return self._connected_edges_predicate(node, self.is_trail_edge)

    def _connected_direct_deviation_edges(self, node):
        """
        Finds the direct deviation edges connected to a node.

        Parameters
        ----------
        node :
            A node key.

        Returns
        -------
        deviation_edges :
            The keys of the connected deviation edges.
            If no deviation edge is attached, the list will be empty.

        Note
        ----
        Direct deviation edges have both end-nodes with equal topological
        distance to a root node. Distances must be precomputed.
        """
        return self._connected_edges_predicate(node, self.is_direct_deviation_edge)

    def _connected_indirect_deviation_edges(self, node):
        """
        Finds the indirect deviation edges connected to a node.

        Parameters
        ----------
        node :
            A node key.

        Returns
        -------
        deviation_edges :
            The keys of the connected deviation edges.
            If no deviation edge is attached, the list will be empty.

        Note
        ----
        Indirect deviation edges have both end-nodes with unequal topological
        distance to a root node. Distances must be precomputed.
        """
        return self._connected_edges_predicate(node, self.is_indirect_deviation_edge)

    def _connected_edges_predicate(self, node, predicate):
        """
        Finds the edges connected to a node.

        Parameters
        ----------
        node :
            A node key.
        predicate :
            A predicate function to search for a specific edge type.

        Returns
        -------
        selected_edges :
            The keys of the selected edges.
            If no edge of the given type is attached, the list will be empty.
        """
        deviation_edges = []
        for edge in self.node_connected_edges(node):
            if predicate(edge):
                deviation_edges.append(edge)
        return deviation_edges

    # ==============================================================================
    # Edges
    # ==============================================================================

    def trail_edges(self, data=False):
        """
        Iterates over the keys of all the trail edges in the diagram.

        Parameters
        ----------
        data :
            `True` if the edges attributes should be yielded simultaneously.
            Defaults to `False`.

        Yields
        -------
        trail_edge :
            The key of the next trail edge.
        attributes :
            The attributes of the next trail edge if `data=True`.
        """
        return self.edges_where({"type": "trail"}, data)

    def deviation_edges(self, data=False):
        """
        Iterates over the keys of all the deviation edges in the diagram.

        Parameters
        ----------
        data :
            `True` if the edges attributes should be yielded simultaneously.
            Defaults to `False`.

        Yields
        -------
        deviation_edge :
            The key of the next deviation edge.
        attributes :
            The attributes of the next deviation edge if `data=True`.
        """
        return self.edges_where({"type": "deviation"}, data)

    def direct_deviation_edges(self, data=False):
        """
        Iterates over the keys of all the direct deviation edges in the diagram.

        Parameters
        ----------
        data :
            `True` if the edges attributes should be yielded simultaneously.
            Defaults to `False`.

        Yields
        -------
        deviation_edge :
            The key of the next direct deviation edge.
        attributes :
            The attributes of the next direct deviation edge if `data=True`.
        """

        def predicate(edge, attr):
            return self.is_direct_deviation_edge(edge)

        return self.edges_where_predicate(predicate, data)

    def indirect_deviation_edges(self, data=False):
        """
        Iterates over the keys of all indirect deviation edges in the diagram.

        Parameters
        ----------
        data :
            `True` if the edges attributes should be yielded simultaneously.
            Defaults to `False`.

        Yields
        -------
        deviation_edge :
            The key of the next indirect deviation edge.
        attributes :
            The attributes of the next indirect deviation edge if `data=True`.
        """

        def predicate(edge, attr):
            return self.is_indirect_deviation_edge(edge)

        return self.edges_where_predicate(predicate, data)

    def auxiliary_trail_edges(self, data=False):
        """
        Iterates over the keys of all trail edges in the auxiliary trails.

        Parameters
        ----------
        data :
            `True` if the edges attributes should be yielded simultaneously.
            Defaults to `False`.

        Yields
        -------
        deviation_edge :
            The key of the next auxiliary trail edge.
        attributes :
            The attributes of the next auxiliary trail edge if `data=True`.
        """

        def predicate(edge, attr):
            return self.is_auxiliary_trail_edge(edge)

        return self.edges_where_predicate(predicate, data)

    # ==============================================================================
    # Node Filters
    # ==============================================================================

    def is_node_origin(self, node):
        """
        Checks if a node is an origin node.

        Parameters
        ----------
        node :
            A node key.

        Returns
        -------
        flag :
            `True`if the node is a origin node.
            `False` otherwise.
        """
        return self.node_attribute(key=node, name="type") == "_origin"

    def is_node_support(self, node):
        """
        Tests if a node is a support node.

        Parameters
        ----------
        node :
            A node key.

        Returns
        -------
        flag :
            `True`if the node is a support node.
            `False` otherwise.
        """
        return self.node_attribute(key=node, name="type") == "support"

    # ==============================================================================
    # Edge Predicates
    # ==============================================================================

    def is_trail_edge(self, edge):
        """
        Tests whether or not an edge is a trail edge.

        Parameters
        ----------
        edge :
            The key of the edge to test.

        Returns
        -------
        flag :
            `True`if the edge is a trail edge. `False` otherwise.
        """
        if self.edge_attribute(edge, "type") == "trail":
            return True
        return False

    def is_deviation_edge(self, edge):
        """
        Tests whether or not an edge is a deviation edge.

        Parameters
        ----------
        edge :
            The key of the edge to test.

        Returns
        -------
        flag :
            `True`if the edge is a deviation edge. `False` otherwise.
        """
        if self.edge_attribute(edge, "type") == "deviation":
            return True
        return False

    def is_auxiliary_trail_edge(self, edge):
        """
        Tests whether or not an edge is the edge of an auxiliary trail.

        Parameters
        ----------
        edge :
            The key of the edge to test.

        Returns
        -------
        flag :
            `True`if the edge is in an auxiliary trail. `False` otherwise.
        """
        aux_trails = set([tuple(edge) for edge in self.auxiliary_trails()])
        if edge in set(aux_trails):
            return True
        return False

    def is_direct_deviation_edge(self, edge):
        """
        Tests if a deviation edge is direct.

        Parameters
        ----------
        edge :
            The key of the edge to test.

        Returns
        -------
        flag :
            `True`if the deviation edge is direct.
            `False` otherwise.
        """

        def predicate(x):
            a, b = self.edge_sequence(edge)
            if a == b:
                return True

        return self._is_deviation_edge_predicate(edge, predicate)

    def is_indirect_deviation_edge(self, edge):
        """
        Tests if a deviation edge is indirect.

        Parameters
        ----------
        edge :
            The key of the edge to test.

        Returns
        -------
        flag :
            `True`if the deviation edge is indirect.
            `False` otherwise.
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
        edge :
            The key of the edge to test.
        predicate :
            A function that for user-defined test conditions.
            Predicate must take in a single edge key as argument.

        Returns
        -------
        flag :
            `True`if the deviation edge meets the predicate condition.
            `False` otherwise.

        Notes
        -----
        Similar to `FormDiagram.edges_where_predicate()`.
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
        node :
            The node key.

        Returns
        -------
        k :
            The sequence key.
        """
        k = self.node_attribute(key=node, name="_k")
        if k is None:
            msg = "Node {} doesn't belong to a sequence yet. Try adding trails first."
            raise ValueError(msg.format(node))
        return k

    def edge_sequence(self, edge):
        """
        Gets the sequence of the nodes of a given edge.

        Parameters
        ----------
        edge :
            The edge key.

        Returns
        -------
        sequences :
            The nodes sequences.
        """
        u, v = edge
        return self.node_sequence(u), self.node_sequence(v)

    def sequences(self, keys=False):
        """
        Iterate over all the sequences in the topology diagram in ascending order.

        Parameters
        ----------
        keys :
            If `True`, yield the trail key alongside the trail.

        Yields
        ------
        sequence :
            The next sequence if `keys` is `False`.
            Otherwise, a tuple with the sequence key and the corresponding node keys.
        """
        for k in range(self.number_of_sequences()):

            def predicate(node, attr):
                return self.node_sequence(node) == k

            sequence = tuple(self.nodes_where_predicate(predicate))
            if not keys:
                yield sequence
            else:
                yield k, sequence

    def number_of_sequences(self):
        """
        The number of sequences in the topology diagram.

        Equivalent to the largest sequence key.

        Returns
        -------
        sequence : `int`
            The number of sequences.
        """
        return self.sequence_last() + 1

    def sequence_last(self):
        """
        The key of the last sequence in the topology diagram.

        Returns
        -------
        key : `int`
            The sequence key.
        """
        return max(list(self.nodes_attribute(name="_k")))

    # ==============================================================================
    # Mappings
    # ==============================================================================

    def trail_sequences(self, key):
        """
        Create a mapping between topological sequences and the nodes in a trail.

        Parameters
        ----------
        key :
            The trail key.

        Returns
        -------
        sequence_map :
            A dictionary wherein keys are sequences and values are node keys.
        """
        sequences = dict()
        for node in self.trail(key):
            sequences[self.node_sequence(node)] = node

        return sequences

    def trails_sequences(self):
        """
        Creates a mapping of mappings between the nodes of the trails and the sequences.

        The mapping has the form `{trail_key: {sequence: node}}`.

        Returns
        -------
        sequences_map :
            A dictionary wherein keys are trail keys and values are dictionaries
            wherein keys are sequences and values are node keys.
        """
        sequences = dict()

        for key, trail in self.trails(keys=True):
            sequences[key] = self.trail_sequences(key)

        return sequences

    # ==============================================================================
    # Magic methods
    # ==============================================================================

    def __repr__(self):
        tpl = "{}(\n\tEdges: {}\n\tTrail edges: {}\n\tDeviation edges: {}\n\tNodes: {}\n\tSupport nodes: {}\n\tLoaded nodes: {}\n\tTrails: {}\n\tAuxiliary trails: {}\n\t)"
        data = [
            self.__class__.__name__,
            self.number_of_edges(),
            self.number_of_trail_edges(),
            self.number_of_deviation_edges(),
            self.number_of_nodes(),
            self.number_of_support_nodes(),
            self.number_of_loaded_nodes(),
            self.number_of_trails(),
            self.number_of_auxiliary_trails(),
        ]
        return tpl.format(*data)


# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
