from compas.datastructures import Network

from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector

from compas_cem.diagrams import NodeMixins
from compas_cem.diagrams import EdgeMixins

__all__ = [
    "Diagram"
]

# ==============================================================================
# Diagram
# ==============================================================================

class Diagram(NodeMixins, EdgeMixins, Network):
    """
    Base class that shares functionality across diagrams.
    """

    def __init__(self, *args, **kwargs):
        super(Diagram, self).__init__(*args, **kwargs)

# ==============================================================================
# Edge Vectors
# ==============================================================================

    def incoming_edge_vectors(self, node, edges, normalize=False):
        """
        Calculates the edge vectors so that they point towards a node.

        Parameters
        ----------
        node : ``int``
            A node key.
        edges : ``list``
            A list of edge keys.
        normalize : ``bool``
            A boolean flag to normalize all the resulting edge vectors.
            Defaults to ``False``.
        
        Returns
        -------
        edge_vectors : ``list``
            A list of xyz vectors.
        """
        vectors = []
        for u, v in edges:
            other_node = u if u != node else v
            vector = self.two_node_vector((other_node, node), normalize)
            vectors.append(vector)

        return vectors


    def two_node_vector(self, nodes, normalize=False):
        """
        Calculates the vector between two nodes in a diagram..

        Parameters
        ----------
        nodes : ``list``
            A list with two node keys.
        normalize : ``bool``
            A boolean flag to normalize all the resulting edge vectors.
            Defaults to ``False``.
        
        Returns
        -------
        vector : ``list``
            The calculated xyz vector. 
        """
        assert len(nodes) == 2, "Supply only two nodes!"
        vector = subtract_vectors(*[self.node_coordinates(n) for n in nodes])
        if not normalize:
            return vector
        return normalize_vector(vector)

# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
