from compas_cem.diagrams import FormDiagram

from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.elements import DeviationEdge

from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport

from compas_cem.equilibrium import force_equilibrium
from compas_cem.equilibrium.force_numpy import force_equilibrium_numpy

from compas_cem.plotters import TopologyPlotter
from compas_cem.plotters import FormPlotter


# ------------------------------------------------------------------------------
# Data
#-------------------------------------------------------------------------------

points = [
    (0, [0.0, 0.0, 0.0]),
    (1, [0.0, 1.0, 0.0]),
    (2, [0.0, 2.0, 0.0]),
    (3, [1.0, 0.0, 0.0]),
    (4, [1.0, 1.0, 0.0]),
    (5, [1.0, 2.0, 0.0])
]

trail_edges = [
    (0, 1),
    (1, 2),
    (3, 4),
    (4, 5)
]

deviation_edges = [
    (1, 4),
    (2, 5)
]

# ------------------------------------------------------------------------------
# Topology Diagram
# ------------------------------------------------------------------------------

topology = FormDiagram()

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
# Collect Trails and Edge lines
# ------------------------------------------------------------------------------

tr = topology.trails()
edge_lines = [topology.edge_coordinates(*edge) for edge in topology.edges()]

# ------------------------------------------------------------------------------
# Force Equilibrium
# ------------------------------------------------------------------------------

form = topology.copy()
force_equilibrium(form, eps=1e-5, kmax=100, verbose=True)

for node in form.support_nodes():
    print(node, form.node_residual(node))

# ------------------------------------------------------------------------------
# Topology Plotter
# ------------------------------------------------------------------------------

plotter = TopologyPlotter(topology, figsize=(16, 9))

plotter.draw_loads(radius=0.025)
plotter.draw_nodes(radius=0.025)
plotter.draw_edges()

plotter.show()

# ------------------------------------------------------------------------------
# Form Plotter
# ------------------------------------------------------------------------------

plotter = FormPlotter(form, figsize=(16, 9))

plotter.draw_nodes(radius=0.025, text="key")
plotter.draw_edges(text="force")
plotter.draw_loads(scale=0.5)
plotter.draw_residuals(scale=0.25)
plotter.draw_segments(edge_lines)

plotter.show()
