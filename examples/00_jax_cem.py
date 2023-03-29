from compas.geometry import Translation

from compas_cem.diagrams import TopologyDiagram

from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.elements import DeviationEdge

from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport

from compas_cem.equilibrium import static_equilibrium

from compas_cem.plotters import Plotter


# ------------------------------------------------------------------------------
# Parameters
# ------------------------------------------------------------------------------

plot = False

# ------------------------------------------------------------------------------
# Instantiate a topology diagram
# ------------------------------------------------------------------------------

topology = TopologyDiagram()

# ------------------------------------------------------------------------------
# Add nodes
# ------------------------------------------------------------------------------

topology.add_node(Node(0, [0.0, 0.0, 0.0]))
topology.add_node(Node(1, [1.0, 0.0, 0.0]))
topology.add_node(Node(2, [2.5, 0.0, 0.0]))
topology.add_node(Node(3, [3.5, 0.0, 0.0]))

# ------------------------------------------------------------------------------
# Add edges
# ------------------------------------------------------------------------------

topology.add_edge(TrailEdge(0, 1, length=-1.5))
topology.add_edge(DeviationEdge(1, 2, force=-1.0))
topology.add_edge(TrailEdge(2, 3, length=-1.5))

# ------------------------------------------------------------------------------
# Add supports
# ------------------------------------------------------------------------------

topology.add_support(NodeSupport(0))
topology.add_support(NodeSupport(3))

# ------------------------------------------------------------------------------
# Add loads
# ------------------------------------------------------------------------------

topology.add_load(NodeLoad(1, [0.0, -1.0, 0.0]))
topology.add_load(NodeLoad(2, [0.0, -1.0, 0.0]))

# ------------------------------------------------------------------------------
# Build trails automatically
# ------------------------------------------------------------------------------

topology.build_trails()

# ------------------------------------------------------------------------------
# Compute a state of static equilibrium
# ------------------------------------------------------------------------------

# form = static_equilibrium(topology, eta=1e-6, tmax=100, verbose=True)

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

from compas.datastructures import network_connectivity_matrix
from compas.utilities import pairwise
import numpy as np
import jax.numpy as jnp
import equinox as eqx

class EquilibriumModel(eqx.Module):
    pass


# ------------------------------------------------------------------------------
# Graph
# ------------------------------------------------------------------------------

def network_incidence_matrix(network):
    """
    Calculate the incidence matrix of a network.
    """
    return np.abs(network_connectivity_matrix(topology))


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

connectivity = network_connectivity_matrix(topology)
incidence = network_incidence_matrix(topology)
incidence_signed = network_signed_incidence_matrix(topology)

print(connectivity)
print(incidence)
print(incidence_signed)

# trails_sequences = topology.trails_sequences()
# trails = {k: v[:] for k, v in topology.trails()}

# ------------------------------------------------------------------------------
# Nodes
# ------------------------------------------------------------------------------

nodes = list(topology.nodes())
node_index = topology.key_index()

# ------------------------------------------------------------------------------
# Edges
# ------------------------------------------------------------------------------

edges = list(topology.edges())
edge_index = topology.uv_index()
index_edge = topology.index_uv()
print(f"{edges=}")

# ------------------------------------------------------------------------------
# Deviation mask
# ------------------------------------------------------------------------------

deviation_mask = []
for edge in edges:
    mask_value = 0
    if topology.is_deviation_edge(edge):
        mask_value = 1
    deviation_mask.append(mask_value)

print(f"{deviation_mask=}")

# ------------------------------------------------------------------------------
# Sequences
# ------------------------------------------------------------------------------

# topology.shift_trail(2, 1)
sequences = np.ones((
                     topology.number_of_sequences(),
                     topology.number_of_trails()),
                    dtype=np.int32)

sequences *= -1  # negate to deal with shifted trails

for tidx, trail in enumerate(topology.trails()):
    for node in trail:
        seq = topology.node_sequence(node)
        sequences[seq][tidx] = node_index[node]

# ------------------------------------------------------------------------------
# Trail lengths - NOTE: outgoing per node
# ------------------------------------------------------------------------------

trail_lengths = np.zeros((topology.number_of_nodes(), 1))

for trail in topology.trails():
    for u, v in pairwise(trail):
        edge = (u, v)
        if edge not in edges:
            edge = (v, u)
        trail_lengths[u] = topology.edge_length_2(edge)

print(f"{trail_lengths=}")

# ------------------------------------------------------------------------------
# Deviation forces
# ------------------------------------------------------------------------------

deviation_forces = np.zeros(topology.number_of_edges())
for i, edge in enumerate(edges):
    if topology.is_deviation_edge(edge):
       deviation_forces[i] = topology.edge_force(edge)
deviation_forces = np.reshape(deviation_forces, (-1, 1))

print(f"{deviation_forces=}")

# ------------------------------------------------------------------------------
# Starting parameters
# ------------------------------------------------------------------------------

loads = list(topology.node_load(node) for node in nodes)
loads = np.asarray(loads)

positions = list(topology.node_coordinates(node) for node in nodes)
positions = np.asarray(positions)
positions_start = np.asarray(positions)

residuals = []
residual = np.zeros((topology.number_of_trails(), 3))

# deviation = np.ones((topology.number_of_trails(), 3)) * -1.0

print(f"{positions=}")

# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

def vector_length(v, axis=1, keepdims=True):
    return np.linalg.norm(v, axis=axis, keepdims=keepdims)

def residual_vector(r, d, q):
    return r - d - q

def position_vector(p, r, l, t):
    return p + l * (r / t)

def trail_force(r):
    return vector_length(r)

def edge_vector(xyz, connectivity):
    vector = connectivity @ xyz
    return vector / vector_length(vector)

def deviation_vector(seq, vectors, incidence, forces):
    incidence_seq = incidence[:, seq]  # (num edges, num nodes seq)
    incident_forces = incidence_seq * forces # (num edges, num nodes seq)

    return incident_forces.T @ vectors

# ------------------------------------------------------------------------------
# Form finding
# ------------------------------------------------------------------------------

# TODO: Create signed incidence matrix, connectivity matrix and deviation mask
# TODO: do we really need the connectivity matrix? all of them are very sparse

print("\n*** Starting form finding ***")
position_start = positions[sequences[0], :]
position_last = position_start

# iterate over sequences
for i, sequence in enumerate(sequences):

    """
    vectors = connectivity @ xyz
    pos, residual = vmap(node_equilibrium)(sequence, xyz, residual, dev_forces)
    """
    print(f"Sequence: {i}")

    load = loads[sequence, :]
    # position_last = positions[sequence, :]
    tlength = trail_lengths[sequence, :]
    # update position matrix
    positions[sequence, :] = position_last

    # NOTE: more efficient to slice and sum?
    # TODO: mask indirect deviation edges when t = 0
    # TODO: implement deviation_vector function
    # deviation = deviation_vector(sequence, positions, adjacency, deviation_mask)
    edge_vecs = edge_vector(positions, connectivity)
    deviation = deviation_vector(sequence,
                                 edge_vecs,
                                 incidence_signed,
                                 deviation_forces)

    # TODO: mask -1 values in sequence #shiftedtrails. before or after equilibrium computation?
    residual = residual_vector(residual, deviation, load)
    residuals.append(residual)

    tforce = trail_force(residual)

    position_new = position_vector(position_last,
                                   residual,
                                   tlength,
                                   tforce)

    print(sequence)
    print(load)
    print(position_last)
    print(f"{position_last=}")
    print("residual\n", residual)
    print("trail force\n", tforce)
    print(f"{position_new=}")

    print()

    # replace last positions with new positions
    position_last = position_new


print(f"{positions_start=}")
print(f"{positions=}")
print("ok")

# ------------------------------------------------------------------------------
# Plot results
# ------------------------------------------------------------------------------

if plot:
    plotter = Plotter()

    # add topology diagram to scene
    artist = plotter.add(topology,
                         nodesize=0.2,
                         nodetext="sequence",
                         nodecolor="sequence",
                         show_nodetext=True)


    # add shifted form diagram to the scene
    # form = form.transformed(Translation.from_vector([0.0, -1.0, 0.0]))
    # plotter.add(form, nodesize=0.2, show_edgetext=True, edgetext="sequence")

    # show plotter contents
    plotter.zoom_extents()
    plotter.show()
