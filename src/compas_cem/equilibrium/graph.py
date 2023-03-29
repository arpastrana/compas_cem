import numpy as np
import jax.numpy as jnp

from typing import Tuple
from typing import NamedTuple

from compas.datastructures import network_connectivity_matrix


__all__ = ["EquilibriumGraph"]


DTYPE_NP_I = np.int64
DTYPE_NP_F = np.float64


# NOTE: Treat this object as a struct or as a standard object?
class EquilibriumGraph(NamedTuple):
    """
    The topological graph of a discrete structure.
    """
    nodes : Tuple
    edges : Tuple
    trail_edges : Tuple
    deviation_edges : Tuple
    sequences : np.array
    # TODO: either incidence or connectivity should go
    incidence : jnp.array
    connectivity : np.array

    def number_of_trails(self):
        return self.sequences.shape[1]

    def number_of_sequences(self):
        return self.sequences.shape[0]

    @classmethod
    def from_topology_diagram(cls, topology):
        """
        Create a equilibrium graph from a COMPAS CEM topology diagram.
        """
        # there must be at least one trail
        assert topology.number_of_trails() > 0, "No trails in the diagram!"

        nodes = tuple(topology.nodes())
        edges = tuple(topology.edges())

        # trail edges
        trail_edges = []
        for edge in edges:
            val = 0.
            if topology.is_trail_edge(edge):
                val = 1.
            trail_edges.append(val)
        trail_edges = np.asarray(trail_edges, dtype=DTYPE_NP_F)

        # deviation edges
        deviation_edges = np.logical_not(trail_edges)

        # sequences
        node_index = topology.key_index()
        sequences = np.ones((topology.number_of_sequences(),
                             topology.number_of_trails()),
                             dtype=DTYPE_NP_I)

        sequences *= -1  # negate to deal with shifted trails

        for tidx, trail in enumerate(topology.trails()):
            for node in trail:
                seq = topology.node_sequence(node)
                sequences[seq][tidx] = node_index[node]

#        sequences = jnp.asarray(sequences)

        # incidence matrix
        # NOTE: converted to jax numpy array. Is a tuple a better choice?
        incidence = jnp.asarray(network_signed_incidence_matrix(topology))

        # connectivity matrix
        connectivity = network_connectivity_matrix(topology)

        return cls(nodes=nodes,
                   edges=edges,
                   trail_edges=trail_edges,
                   deviation_edges=deviation_edges,
                   sequences=sequences,
                   incidence=incidence,
                   connectivity=connectivity)


def network_incidence_matrix(network):
    """
    Calculate the incidence matrix of a network.
    """
    return np.abs(network_connectivity_matrix(network))


def network_signed_incidence_matrix(network):
    """
    Compute the signed incidence matrix of a network.
    """
    node_index = network.key_index()
    edge_index = network.uv_index()
    incidence = network_incidence_matrix(network)

    for node in network.nodes():
        i = node_index[node]

        for edge in network.connected_edges(node):
            j = edge_index[edge]
            val = 1.
            if edge[0] != node:
                val = -1.
            incidence[j, i] = val

    return incidence
