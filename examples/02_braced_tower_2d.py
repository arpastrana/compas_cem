from compas.geometry import Translation

from compas_cem.diagrams import TopologyDiagram

from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.elements import DeviationEdge

from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport

from compas_cem.equilibrium import static_equilibrium

from compas_cem.plotters import Plotter


# -------------------------------------------------------------------------------
# Data
# -------------------------------------------------------------------------------

points = [(0, [0.0, 0.0, 0.0]),
          (1, [0.0, 1.0, 0.0]),
          (2, [0.0, 2.0, 0.0]),
          (3, [1.0, 0.0, 0.0]),
          (4, [1.0, 1.0, 0.0]),
          (5, [1.0, 2.0, 0.0])]

trail_edges = [(0, 1),
               (1, 2),
               (3, 4),
               (4, 5)]

deviation_edges = [(1, 4),
                   (2, 5)]

# ------------------------------------------------------------------------------
# Topology Diagram
# ------------------------------------------------------------------------------

topology = TopologyDiagram()

# ------------------------------------------------------------------------------
# Add Nodes
# ------------------------------------------------------------------------------

for key, point in points:
    topology.add_node(Node(key, point))

# ------------------------------------------------------------------------------
# Add Trail Edges
# ------------------------------------------------------------------------------

for u, v in trail_edges:
    topology.add_edge(TrailEdge(u, v, length=-1.0))

# ------------------------------------------------------------------------------
# Add Deviation Edges
# ------------------------------------------------------------------------------

for u, v in deviation_edges:
    topology.add_edge(DeviationEdge(u, v, force=-1.0))

# ------------------------------------------------------------------------------
# Add Indirect Deviation Edges
# ------------------------------------------------------------------------------

topology.add_edge(DeviationEdge(1, 5, force=1.0))
topology.add_edge(DeviationEdge(1, 3, force=1.0))
topology.add_edge(DeviationEdge(2, 4, force=1.0))

# ------------------------------------------------------------------------------
# Set Supports Nodes
# ------------------------------------------------------------------------------

topology.add_support(NodeSupport(0))
topology.add_support(NodeSupport(3))

# ------------------------------------------------------------------------------
# Add Loads
# ------------------------------------------------------------------------------

load = [0.0, -1.0, 0.0]
topology.add_load(NodeLoad(2, load))
topology.add_load(NodeLoad(5, load))

# ------------------------------------------------------------------------------
# Equilibrium of forces
# ------------------------------------------------------------------------------

topology.build_trails()
form = static_equilibrium(topology, eta=1e-6, tmax=100, verbose=True)

# ------------------------------------------------------------------------------
# Plotter
# ------------------------------------------------------------------------------

plotter = Plotter()

# ------------------------------------------------------------------------------
# Plot topology diagram
# ------------------------------------------------------------------------------

plotter.add(topology, nodesize=0.2)

# ------------------------------------------------------------------------------
# Plot translated form diagram
# ------------------------------------------------------------------------------

plotter.add(form.transformed(Translation.from_vector([2.0, 0.0, 0.0])),
            nodesize=0.2,
            loadscale=0.5,
            reactionscale=0.5)

# ------------------------------------------------------------------------------
# Plot scene
# -------------------------------------------------------------------------------

plotter.zoom_extents()
plotter.show()
