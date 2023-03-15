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

topology.add_edge(TrailEdge(0, 1, length=-1.0))
topology.add_edge(DeviationEdge(1, 2, force=-1.0))
topology.add_edge(TrailEdge(2, 3, length=-1.0))

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
# Compute a state of static equilibrium
# ------------------------------------------------------------------------------

import numpy as np
import equinox as eqx

class EquilibriumModel(eqx.Module):
    pass


# trails_sequences = topology.trails_sequences()
# trails = {k: v[:] for k, v in topology.trails()}

nodes = list(topology.nodes())
node_index = topology.key_index()


# topology.shift_trail(2, 1)
sequences = np.ones((
                     topology.number_of_sequences(),
                     topology.number_of_trails()),
                    dtype=np.int32)
sequences *= -1

for tidx, trail in enumerate(topology.trails()):
    for node in trail:
        seq = topology.node_sequence(node)
        sequences[seq][tidx] = node_index[node]

# print(sequences)
loads = list(topology.node_load(node) for node in nodes)
loads = np.asarray(loads)
print(f"loads shape: {loads.shape}")

positions = list(topology.node_coordinates(node) for node in nodes)
positions = np.asarray(positions)
print(f"positions shape: {positions.shape}")

residuals = []
residual = np.zeros((topology.number_of_trails(), 3))
print(f"residual shape: {residual.shape}")

deviation = np.zeros((topology.number_of_trails(), 3))

def residual_vector(r, d, q):
    return r - d - q

def position_vector(p, r, l, t):
    return p + l * (r / t)

def trail_force(r):
    return np.linalg.norm(residual, axis=1, keepdims=True)


# iterate over sequences
for sequence in sequences:
    load = loads[sequence, :]
    position_last = positions[sequence, :]

    # deviation = deviation_vector(sequence, positions, adjacency, deviation_mask)
    residual = residual_vector(residual, deviation, load)
    residuals.append(residual)

    tforce = trail_force(residual)
    tlength = 1.

    position_new = position_vector(position_last, residual, tlength, tforce)


    print(sequence)
    print(load)
    print(position_last)
    print(f"{position_last=}")
    print("residual\n", residual)
    print("trail force\n", tforce)
    print(f"{position_new=}")

    print()
    position_last = position_new

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
