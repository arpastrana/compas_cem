import jax

import numpy as np
import jax.numpy as jnp

from jax import vmap

import equinox as eqx

from compas.utilities import pairwise

from compas_cem.equilibrium import EquilibriumState


class EquilibriumModel(eqx.Module):
    """
    An equilibrium model that implements the combinatorial equilibrium modeling (CEM) framework.

    Parameters
    ----------
    topology : `compas_cem.diagrams.TopologyDiagram`
        A valid topology diagram.
    """
    xyz: jnp.array  # TODO: N x 3 or A x 3?
    lengths : jnp.array  # M x 1 or B x 1?
    forces : jnp.array  # M x 1  or C x 1?
    loads : jnp.array  # N x 3
    # planes  : jnp.array  (static!)

    @classmethod
    def from_topology_diagram(cls, topology):
        """
        Create an equilibrium model from a COMPAS CEM topology diagram.
        """
        loads = jnp.asarray([topology.node_load(node) for node in topology.nodes()])
        xyz = jnp.asarray([topology.node_coordinates(node) for node in topology.nodes()])
        forces = jnp.reshape(jnp.asarray([topology.edge_force(edge) for edge in topology.edges()]), (-1, 1))
        # lengths = jnp.reshape(jnp.asarray([topology.edge_length_2(edge) for edge in topology.edges()]), (-1, 1))

        # TODO: find a way to treat edge lengths per edge, not per node
        lengths = np.zeros((topology.number_of_nodes(), 1))
        edges = list(topology.edges())
        for trail in topology.trails():
            for u, v in pairwise(trail):
                edge = (u, v)
                if edge not in edges:
                    edge = (v, u)
                lengths[u, :] = topology.edge_length_2(edge)
        lengths = jnp.asarray(lengths)

        return cls(xyz, lengths, forces, loads)

    def __call__(self, topology):
        """
        Compute an equilibrium state.

        The computation follows the combinatorial equilibrium modeling (CEM) form-finding algorithm.
        """
        xyz = jnp.zeros((len(topology.nodes), 3))
        residuals = jnp.zeros((topology.number_of_trails(), 3))

        # for t in range(kmax)...
        sequence_origin = topology.sequences[0]
        xyz_seq = self.xyz[sequence_origin, :]

        for i, sequence in enumerate(topology.sequences):

            # update position matrix
            xyz = xyz.at[sequence, :].set(xyz_seq)

            # edge vectors
            vectors = self.edge_vectors(xyz, topology.connectivity, True)
            residuals, xyz_seq = self.nodes_equilibrium(sequence,
                                                        residuals,
                                                        xyz,
                                                        vectors,
                                                        topology)
            # compute trail lengths
            forces = self.trail_forces(residuals)

        # edge lengths
        vectors = self.edge_vectors(xyz, topology.connectivity)
        lengths = self.edges_length(vectors)

        return EquilibriumState(xyz=xyz,
                                reaction_forces=residuals,
                                lengths=lengths,
                                forces=forces)


    def nodes_equilibrium(self, *args, **kwargs):
        """
        Calculate equilibrium at one node of a topology diagram. Vectorized.
        """
        return vmap(self.node_equilibrium, in_axes=(0, 0, None, None, None))(*args, **kwargs)

    def node_equilibrium(self, index, residual, xyz, vectors, topology):
        """
        Calculate equilibrium at one node of a topology diagram.
        """
        load = self.loads[index, :]
        position = xyz[index, :]
        length = self.lengths[index, :]

        incidence = topology.incidence[:, index]
        incidence = np.reshape(incidence, (-1, 1))

        # length = self.trail_length(self.lengths, incidence)
        deviation = self.deviation_vector(self.forces, vectors, incidence).flatten()
        residual = self.residual_vector(residual, deviation, load)
        position = self.position_vector(position, residual, length)

        return residual, position

    @staticmethod
    def deviation_vector(deviation_forces, vectors, incidence):
        """
        Calculate the resultant deviation vector incoming to a node.
        """
        incident_forces = incidence * deviation_forces  # (num edges, num nodes seq)
        return incident_forces.T @ vectors

    @staticmethod
    def trail_length(trail_lengths, incidence):
        """
        Get the length of the next trail edge outgoing from a node.
        """
        incident_length = incidence * trail_lengths  # (num_edges, num_nodes)

    @staticmethod
    def residual_vector(residual, deviation, load):
        """
        The updated residual vector at a node.
        """
        return residual - deviation - load

    @staticmethod
    def position_vector(position, residual, trail_length):
        """
        The position of the next node on a trail.
        """
        return position + trail_length * (residual / vector_length(residual, axis=None))

    @staticmethod
    def trail_forces(residual):
        """
        The force passing through a trail edge.
        """
        return vector_length(residual)

    @staticmethod
    def edge_vectors(xyz, connectivity, normalize=False):
        """
        The edge vectors of the graph.
        """
        vector = connectivity @ xyz
        if not normalize:
            return vector
        return vector / vector_length(vector)

    @staticmethod
    def edges_length(edge_vectors):
        """
        The edge length.
        """
        return vector_length(edge_vectors)

# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------

def vector_length(v, axis=1, keepdims=True):
    """
    Calculate the length of a vector
    """
    return jnp.linalg.norm(v, axis=axis, keepdims=keepdims)



if __name__ == "__main__":
    # eqstate = model(topology)
    pass
