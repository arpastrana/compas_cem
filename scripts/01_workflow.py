from compas.geometry import add_vectors
from compas.geometry import length_vector
from compas.geometry import scale_vector
from compas.geometry import normalize_vector

from compas_cem.diagrams import TopologyDiagram
from compas_cem.equilibrium import force_equilibrium

from compas_plotters import NetworkPlotter

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
    (2, 5),
    (1, 4)
]

# ------------------------------------------------------------------------------
# Topology Diagram
# ------------------------------------------------------------------------------

topology = TopologyDiagram()

# ------------------------------------------------------------------------------
# Add Nodes
# ------------------------------------------------------------------------------

for i, xyz in vertices:
    topology.add_node(key=i, x=xyz[0], y=xyz[1], z=xyz[2])

# ------------------------------------------------------------------------------
# Add Trail Edges
# ------------------------------------------------------------------------------

for edge in trail_edges:
    u, v = edge
    topology.add_edge(u, v, type="trail", comb_state=-1, length=1.0)

# ------------------------------------------------------------------------------
# Add Deviation Edges
# ------------------------------------------------------------------------------

topology.add_edge(2, 5, type="deviation", comb_state=1, force=1.0)
topology.add_edge(1, 4, type="deviation", comb_state=1, force=1.0)

# ------------------------------------------------------------------------------
# Add Root Nodes
# ------------------------------------------------------------------------------

topology.nodes_attribute("type", "root", [2, 5])
topology.node_attributes(2, ["x", "y", "z"], vertices[2][1])
topology.node_attributes(5, ["x", "y", "z"], vertices[5][1])

# ------------------------------------------------------------------------------
# Add Supports Nodes
# ------------------------------------------------------------------------------

topology.nodes_attribute("type", "support", [0, 3])

# ------------------------------------------------------------------------------
# Add Point Loads
# ------------------------------------------------------------------------------

load = [0.0, -1.0, 0.0]
for q, attr in zip(load, ["qx", "qy", "qz"]):
    topology.nodes_attribute(attr, q, [2, 5])

# ------------------------------------------------------------------------------
# Trails
# ------------------------------------------------------------------------------

tr = topology.trails()

# ------------------------------------------------------------------------------
# Initial Edges
# ------------------------------------------------------------------------------

initial_edges = [topology.edge_coordinates(*edge) for edge in topology.edges()]

# ------------------------------------------------------------------------------
# Force Equilibrium
# ------------------------------------------------------------------------------

force_equilibrium(topology)

# ------------------------------------------------------------------------------
# Visualization
# ------------------------------------------------------------------------------

plotter = NetworkPlotter(topology, figsize=(16, 9))

# nodes
# blue for trails, green for deviation
cmap = {"support": (255, 0, 0), "root": (255, 255, 0), "d": (255, 255, 255)}
nodecolors = {n: cmap[attr.get("type", "d")] for n, attr in topology.nodes(True)}
plotter.draw_nodes(radius=0.03, text="key", facecolor=nodecolors)

# edges
# blue for trails, green for deviation
colormap = {"trail": (255, 0, 255), "deviation": (0, 255, 0)}
edgecolors = {e: colormap[attr["type"]] for e, attr in topology.edges(True)}
plotter.draw_edges(text="key", color=edgecolors)

# arrows
scale_factor = 0.5
arrows = []
for node, attr in topology.nodes(True):

    q_vec = topology.node_attributes(node, ["qx", "qy", "qz"])
    if length_vector(q_vec) < 1e-3:
        continue

    arrow = {}
    arrow["end"] = topology.node_coordinates(node)
    arrow["start"] = add_vectors(arrow["end"], scale_vector(normalize_vector(q_vec), -scale_factor))
    arrow["color"] = (0, 0, 0)
    arrow["width"] = 4.0
    
    arrows.append(arrow)

plotter.draw_arrows(arrows)

# initial lines
lines = []

for edge in initial_edges:
    line = {}

    start, end = edge
    line["start"] = start
    line["end"] = end
    
    line["color"] = (40, 40, 40)
    line["width"] = 0.5

    lines.append(line)

plotter.draw_lines(lines)

# show
plotter.show()
