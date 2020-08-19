from compas_cem.diagrams import TopologyDiagram
from compas_cem.plotters import TopologyPlotter

from compas_cem.equilibrium import force_equilibrium

from compas.utilities import geometric_key

# ------------------------------------------------------------------------------
# Data
#-------------------------------------------------------------------------------

vertices = [
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

topology = TopologyDiagram()

# ------------------------------------------------------------------------------
# Add Nodes
# ------------------------------------------------------------------------------

for node, xyz in vertices:
    topology.add_node_from_xyz(node, xyz)

# ------------------------------------------------------------------------------
# Add Trail Edges
# ------------------------------------------------------------------------------

for edge in trail_edges:
    topology.add_trail_edge(edge, length=-1.0)

# ------------------------------------------------------------------------------
# Add Deviation Edges
# ------------------------------------------------------------------------------

for edge in deviation_edges:
    topology.add_deviation_edge(edge, force=-1.0)

# ------------------------------------------------------------------------------
# Add Indirect Deviation Edges
# ------------------------------------------------------------------------------

# topology.add_deviation_edge((1, 5), force=1.0)
# topology.add_deviation_edge((1, 3), force=1.0)
# topology.add_deviation_edge((2, 4), force=1.0)

# ------------------------------------------------------------------------------
# Set Root Nodes
# ------------------------------------------------------------------------------

topology.root(2)
topology.root(5)

# ------------------------------------------------------------------------------
# Set Supports Nodes
# ------------------------------------------------------------------------------

topology.support(0)
topology.support(3)

# ------------------------------------------------------------------------------
# Add Loads
# ------------------------------------------------------------------------------

load = [0.0, -1.0, 0.0]
topology.node_load(2, load)
topology.node_load(5, load)

# ------------------------------------------------------------------------------
# Collect Trails and Edge lines
# ------------------------------------------------------------------------------

tr = topology.trails()
edge_lines = [topology.edge_coordinates(*edge) for edge in topology.edges()]

# ------------------------------------------------------------------------------
# Force Equilibrium
# ------------------------------------------------------------------------------

force_equilibrium(topology, eps=1e-5, kmax=100, verbose=True)

# ------------------------------------------------------------------------------
# Visualization
# ------------------------------------------------------------------------------

edge_text = {e: round(attr.get("force", attr.get("length")), 3) for e, attr in topology.edges(True)}

edge_text = {}
for e, attr in topology.deviation_edges(True):
    edge_text[e] = round(attr["length"], 3)
for e, attr in topology.trail_edges(True):
    edge_text[e] = round(attr["force"], 3)

node_text = {n: geometric_key(topology.node_coordinates(n), precision="3f") for n in topology.nodes()}
node_text = None

plotter = TopologyPlotter(topology, figsize=(16, 9))

plotter.draw_nodes(radius=0.03, text=node_text)
plotter.draw_edges(text=edge_text)
plotter.draw_loads()
plotter.draw_segments(edge_lines)

plotter.show()
