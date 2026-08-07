from compas.data import Data
from compas.datastructures import Graph
from compas.geometry import length_vector
from compas.tolerance import TOL

from compas_cem.elements import Edge
from compas_cem.elements import Node

__all__ = ["Diagram"]


# ==============================================================================
# Diagram
# ==============================================================================


class Diagram(Graph):
    """
    Base class that shares functionality across diagrams.
    """

    def __init__(self, *args, **kwargs):
        super(Diagram, self).__init__(*args, **kwargs)

        self.update_default_node_attributes(
            {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "qx": 0.0,
                "qy": 0.0,
                "qz": 0.0,
                "rx": 0.0,
                "ry": 0.0,
                "rz": 0.0,
                "_k": None,
                "type": None,
            }
        )

        self.update_default_edge_attributes({"type": None, "length": 0.0, "force": 0.0})

        self.attributes["gkey_node"] = {}
        self.attributes["tol"] = 3

    # ==============================================================================
    # Properties
    # ==============================================================================

    @property
    def tol(self):
        """
        The number of decimal places used to compare node coordinates.
        """
        return self.attributes["tol"]

    @tol.setter
    def tol(self, tol):
        self.attributes["tol"] = tol

    @property
    def gkey_node(self):
        """
        A dictionary that maps geometric keys to node keys.

        Notes
        -----
        This shadows the base graph method of the same name. The mapping here is
        a cache maintained as elements are added, rather than one recomputed from
        the current node coordinates on every call.
        """
        return self.attributes["gkey_node"]

    # ==============================================================================
    # Elements
    # ==============================================================================

    def add_node(self, node=None, key=None, attr_dict=None, **kwattr):
        """
        Add a node to the diagram, from a node element or from a key.

        Parameters
        ----------
        node :
            A node element, or a node key given positionally.
        key :
            A node key. If `None`, the next available key is assigned.
        attr_dict :
            The attributes to store on the node.
        **kwattr :
            Extra attributes to store on the node.

        Returns
        -------
        key :
            The key of the added node.

        Notes
        -----
        This accepts both vocabularies. A node element carries its own
        coordinates and is indexed by its geometric key, which is how a diagram
        is authored. A bare key with attributes is how the base graph adds a
        node, and how deserialization replays one.
        """
        if isinstance(node, Node):
            return self._add_node_element(node)

        if isinstance(node, Edge):
            raise TypeError("an edge element must be added with add_edge")

        if node is not None:
            if key is not None:
                raise ValueError("a node key was given both positionally and by name")
            key = node

        if isinstance(key, Data):
            raise TypeError(f"{key!r} is not a node key")

        return super(Diagram, self).add_node(key=key, attr_dict=attr_dict, **kwattr)

    def add_edge(self, edge=None, v=None, attr_dict=None, **kwattr):
        """
        Add an edge to the diagram, from an edge element or from two node keys.

        Parameters
        ----------
        edge :
            An edge element, or the first node of the edge given positionally.
        v :
            The second node of the edge, when the first was given as a key.
        attr_dict :
            The attributes to store on the edge.
        **kwattr :
            Extra attributes to store on the edge.

        Returns
        -------
        key :
            The two node keys of the added edge.

        Notes
        -----
        This accepts both vocabularies, as `add_node` does. An edge element
        carries its own attributes and may name its end nodes by coordinates,
        creating them if no node sits there yet.
        """
        if isinstance(edge, Edge):
            if v is not None:
                raise ValueError("an edge element already names both of its nodes")
            return self._add_edge_element(edge)

        if isinstance(edge, Node):
            raise TypeError("a node element must be added with add_node")

        return super(Diagram, self).add_edge(edge, v, attr_dict=attr_dict, **kwattr)

    def _add_node_element(self, node):
        """
        Add a node element and index it by its geometric key.
        """
        xyz = node.xyz
        x, y, z = xyz

        key = super(Diagram, self).add_node(key=node.key, x=x, y=y, z=z)
        self.gkey_node[self.gkey(xyz)] = key

        return key

    def _add_edge_element(self, edge):
        """
        Add an edge element, creating any of its end nodes that do not exist yet.
        """
        edge_keys = []

        for node in edge:
            key = self.node_key(node)

            if key is None:
                key = self._add_node_element(Node(xyz=node))

            edge_keys.append(key)

        u, v = edge_keys
        attr = {k: v for k, v in edge.attributes.items()}

        return super(Diagram, self).add_edge(u, v, attr_dict=attr)

    # ==============================================================================
    # Node lookups
    # ==============================================================================

    def node_exists(self, value):
        """
        Check whether a node key or a point resolves to a node in the diagram.

        Parameters
        ----------
        value :
            A node key, or the xyz coordinates of a point.

        Returns
        -------
        flag :
            `True` if the value resolves to a node. `False` otherwise.
        """
        if self.node_key(value) is not None:
            return True
        return False

    def node_key(self, value):
        """
        Resolve a node key or a point to a node key.

        Parameters
        ----------
        value :
            A node key, or the xyz coordinates of a point.

        Returns
        -------
        key :
            The node key, or `None` if no node sits at the given point.

        Notes
        -----
        An integer is taken to be a node key and is returned unchanged, whether
        or not a node with that key exists.
        """
        if isinstance(value, int):
            return value
        return self.gkey_node.get(self.gkey(value))

    def update_node_xyz(self, key, xyz):
        """
        Move a node to new coordinates and reindex its geometric key.

        Parameters
        ----------
        key :
            A node key.
        xyz :
            The new xyz coordinates of the node.
        """
        gkey = self.gkey(xyz)
        if gkey in self.gkey_node:
            del self.gkey_node[gkey]
        self._add_node_element(Node(key, xyz))

    def node_xyz(self, key, xyz=None):
        """
        Get or set the coordinates of a node.

        Parameters
        ----------
        key :
            A node key.
        xyz :
            The new xyz coordinates of the node. If `None`, the current
            coordinates are returned instead.

        Returns
        -------
        xyz :
            The coordinates of the node, or `None` when setting them.
        """
        if xyz is None:
            return self.node_coordinates(key)
        self.update_node_xyz(key, xyz)

    def gkey(self, xyz):
        """
        Compute the geometric key of a point at the tolerance of the diagram.

        Parameters
        ----------
        xyz :
            The xyz coordinates of a point.

        Returns
        -------
        gkey :
            The geometric key of the point.
        """
        return TOL.geometric_key(xyz, self.tol)

    # ==============================================================================
    # Edge collections
    # ==============================================================================

    def node_connected_edges(self, node):
        """
        The edges incident to a node.

        Parameters
        ----------
        node :
            A node key.

        Returns
        -------
        edges :
            The keys of the edges connected to the node.

        Notes
        -----
        Each edge is reported in the direction it is stored in, so that the key
        returned here can be used to look edge attributes up directly.
        """
        edges = []

        for neighbor in self.neighbors(node):
            if neighbor in self.edge[node]:
                edges.append((node, neighbor))
            else:
                edges.append((neighbor, node))

        return edges

    # ==============================================================================
    #  Node collections
    # ==============================================================================

    def support_nodes(self):
        """
        Nodes where a support has been assigned.

        Yields
        ------
        support_node :
            The key of the next node with a support.
        """
        return self.nodes_where({"type": "support"})

    def loaded_nodes(self, min_force=1e-6):
        """
        Iterate over all the nodes with a large-enough load applied.

        Parameters
        ----------
        min_force :
            The minimum force magnitude to consider a node loaded.

        Yields
        ------
        loaded_node :
            The key of the next loaded node.
        """
        for node in self.nodes():
            if self.is_node_loaded(node, min_force):
                yield node

    # ==============================================================================
    # Counters
    # ==============================================================================

    def number_of_support_nodes(self):
        """
        Number of nodes in the diagram with an assigned support.

        Returns
        -------
        number :
            The number of nodes with a support.
        """
        return len(list(self.support_nodes()))

    def number_of_loaded_nodes(self):
        """
        Number of nodes in the diagram where a load is applied.

        Returns
        -------
        number :
            The number of nodes with an applied load.
        """
        return len(list(self.loaded_nodes()))

    # ==============================================================================
    # Node Filters
    # ==============================================================================

    def is_node_support(self, node):
        """
        Check if a node is a support.

        Parameters
        ----------
        node :
            A node key.

        Returns
        -------
        flag :
            `True` if the node is a support. `False` otherwise.
        """
        return self.node_attribute(key=node, name="type") == "support"

    def is_node_loaded(self, node, min_force=1e-6):
        """
        Check if there is a large-enough load applied to a node.

        Parameters
        ----------
        node :
            A node key.
        min_force :
            The minimum force magnitude to consider a node loaded.

        Returns
        -------
        flag :
            `True` if the node is loaded. `False` otherwise.
        """
        return length_vector(self.node_load(node)) > min_force

    # ==============================================================================
    # Edge Filters
    # ==============================================================================

    def is_edge_supported(self, edge):
        """
        Check if any of the nodes of an edge is a support.

        Parameters
        ----------
        edge :
            An edge key.

        Returns
        -------
        flag :
            `True` if any of the edge nodes is a support. `False` otherwise.
        """
        return any([self.is_node_support(node) for node in edge])

    # ==============================================================================
    # Node Attributes
    # ==============================================================================

    def node_load(self, node):
        """
        Get the load applied at a node.

        Parameters
        ----------
        node :
            A node key.

        Returns
        -------
        load_vector :
            A vector with the xyz components of the load.
        """
        return self.node_attributes(key=node, names=["qx", "qy", "qz"])

    def reaction_force(self, node):
        """
        Get the reaction force vector at a node.

        Parameters
        ----------
        node :
            A node key.

        Returns
        -------
        reaction_vector :
            A vector with the xyz components of the reaction force.
        """
        return self.node_attributes(key=node, names=["rx", "ry", "rz"])

    # ==============================================================================
    # Edge Attributes
    # ==============================================================================

    def edge_force(self, edge):
        """
        Get the force value at an edge.

        Parameters
        ----------
        edge :
            An edge key.

        Returns
        -------
        force :
            The force value in the edge. Negative in compression, positive in
            tension.
        """
        return self.edge_attribute(key=edge, name="force")

    def edge_length_2(self, edge):
        """
        Get the stored length attribute of an edge.

        Parameters
        ----------
        edge :
            An edge key.

        Returns
        -------
        length :
            The signed length of the edge.

        Notes
        -----
        This is the length carried as an edge attribute, which is signed and set
        by the user, not the distance between the two end nodes.
        """
        return self.edge_attribute(key=edge, name="length")

    def edge_plane(self, edge):
        """
        Get the projection plane at an edge.

        Parameters
        ----------
        edge :
            An edge key.

        Returns
        -------
        plane :
            The projection plane of the edge, or `None` if it has none.
        """
        return self.edge_attribute(key=edge, name="plane")

    # ==============================================================================
    # Magic methods
    # ==============================================================================

    def __repr__(self):
        tpl = "{}(\n\tEdges: {}\n\tNodes: {}\n\tSupport Nodes: {}\n\tLoaded nodes: {}\n\t)"
        data = [
            self.__class__.__name__,
            self.number_of_edges(),
            self.number_of_nodes(),
            self.number_of_support_nodes(),
            self.number_of_loaded_nodes(),
        ]
        return tpl.format(*data)

    def __str__(self):
        return self.__repr__()


# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
