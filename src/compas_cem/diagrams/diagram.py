from compas.datastructures import Network

from compas.geometry import length_vector

from compas_cem.diagrams import NodeMixins
from compas_cem.diagrams import EdgeMixins


__all__ = ["Diagram"]


# ==============================================================================
# Diagram
# ==============================================================================


class Diagram(NodeMixins, EdgeMixins, Network):
    """
    Base class that shares functionality across diagrams.
    """
    def __init__(self, *args, **kwargs):
        super(Diagram, self).__init__(*args, **kwargs)

        self.update_default_node_attributes({"x": 0.0,
                                             "y": 0.0,
                                             "z": 0.0,
                                             "qx": 0.0,
                                             "qy": 0.0,
                                             "qz": 0.0,
                                             "rx": 0.0,
                                             "ry": 0.0,
                                             "rz": 0.0,
                                             "_k": None,
                                             "type": None})

        self.update_default_edge_attributes({"type": None,
                                             "length": 0.0,
                                             "force": 0.0})

        self.attributes["gkey_node"] = {}
        self.attributes["tol"] = "3f"

# ==============================================================================
# Properties
# ==============================================================================

    @property
    def tol(self):
        """
        The floating point tolerance for the node coordinates of the diagram.
        Defaults to 0.001.
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
        A dictionary that maps geometric keys to node keys.
        """
        return self.attributes["gkey_node"]

# ==============================================================================
#  Node collections
# ==============================================================================

    def support_nodes(self):
        """
        Nodes whose position is meant to be fixed in space.

        Yields
        -------
        support_node : ``int``
            The key of the next support node.
        """
        return self.nodes_where({"type": "support"})

    def loaded_nodes(self, min_force=1e-6):
        """
        Iterates over all the nodes with a large-enough load applied.

        Parameters
        ----------
        min_force : ``float``
            The minimum force magnitude to consider a node loaded.
            Defaults to ``1e-6``.

        Yields
        -------
        loaded_node : ``int``
            The key of the next loaded node.
        """
        for node in self.nodes():
            if self.is_node_loaded(node, min_force):
                yield node

# ==============================================================================
# Node Filters
# ==============================================================================

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

    def is_node_loaded(self, node, min_force=1e-6):
        """
        Checks if there is a large-enough load applied to a node.

        Parameters
        ----------
        node : ``int``
            A node key.
        min_force : ``float``
            The minimum force magnitude to consider a node loaded.
            Defaults to ``1e-6``.
        Returns
        -------
        flag : ``bool``
            ``True``if the node is a support. ``False`` otherwise.
        """
        return length_vector(self.node_load(node)) > min_force

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

        Returns
        -------
        load_vector: ``list``
            A vector with xyz components of the load.
        """
        return self.node_attributes(key=node, names=["qx", "qy", "qz"])

    def reaction_force(self, node):
        """
        Gets the reaction force vector at a node support.

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

    def edge_length_2(self, edge):
        """
        Gets the length of an edge.

        Parameters
        ----------
        edge : ``tuple``
            The u, v edge key.

        Return
        ------
        length : ``float``
            The edge length.
        """
        return self.edge_attribute(key=edge, name="length")

# ==============================================================================
# Edge Vectors
# ==============================================================================

#     def incoming_edge_vectors(self, node, edges, normalize=False):
#         """
#         Calculates the edge vectors so that they point towards a node.

#         Parameters
#         ----------
#         node : ``int``
#             A node key.
#         edges : ``list``
#             A list of edge keys.
#         normalize : ``bool``
#             A boolean flag to normalize all the resulting edge vectors.
#             Defaults to ``False``.

#         Returns
#         -------
#         edge_vectors : ``list``
#             A list of xyz vectors.
#         """
#         vectors = []
#         for u, v in edges:
#             other_node = u if u != node else v
#             vector = self.two_node_vector((other_node, node), normalize)

#             if normalize:
#                 vector = normalize_vector(vector)

#             vectors.append(vector)

#         return vectors


#     def two_node_vector(self, nodes, normalize=False):
#         """
#         Calculates the vector between two nodes in a diagram.

#         Parameters
#         ----------
#         nodes : ``list``
#             A list with two node keys.
#         normalize : ``bool``
#             A boolean flag to normalize all the resulting edge vectors.
#             Defaults to ``False``.

#         Returns
#         -------
#         vector : ``list``
#             The calculated xyz vector.
#         """
#         assert len(nodes) == 2, "Supply only two nodes!"
#         vector = subtract_vectors(*[self.node_coordinates(n) for n in nodes])
#         if not normalize:
#             return vector
#         return normalize_vector(vector)

# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
