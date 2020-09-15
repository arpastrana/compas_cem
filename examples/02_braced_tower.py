from compas_cem.diagrams import FormDiagram

from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.elements import DeviationEdge

from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport

from compas_cem.equilibrium import force_equilibrium

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
# Form Diagram
# ------------------------------------------------------------------------------

form = FormDiagram()

# ------------------------------------------------------------------------------
# Add Nodes
# ------------------------------------------------------------------------------

for key, point in points:
    form.add_node(Node(key, point))

# ------------------------------------------------------------------------------
# Add Trail Edges
# ------------------------------------------------------------------------------

for u, v in trail_edges:
    form.add_edge(TrailEdge(u, v, length=-1.0))

# ------------------------------------------------------------------------------
# Add Deviation Edges
# ------------------------------------------------------------------------------

for u, v in deviation_edges:
    form.add_edge(DeviationEdge(u, v, force=-1.0))
    
# ------------------------------------------------------------------------------
# Add Indirect Deviation Edges
# ------------------------------------------------------------------------------

form.add_edge(DeviationEdge(1, 5, force=1.0))
form.add_edge(DeviationEdge(1, 3, force=1.0))
form.add_edge(DeviationEdge(2, 4, force=1.0))

# ------------------------------------------------------------------------------
# Set Supports Nodes
# ------------------------------------------------------------------------------

form.add_support(NodeSupport(0))
form.add_support(NodeSupport(3))

# ------------------------------------------------------------------------------
# Add Loads
# ------------------------------------------------------------------------------

load = [0.0, -1.0, 0.0]
form.add_load(NodeLoad(2, load))
form.add_load(NodeLoad(5, load))

# ------------------------------------------------------------------------------
# Collect Trails and Edge lines
# ------------------------------------------------------------------------------

tr = form.trails()
edge_lines = [form.edge_coordinates(*edge) for edge in form.edges()]

# ------------------------------------------------------------------------------
# Force Equilibrium
# ------------------------------------------------------------------------------

force_equilibrium(form, eps=1e-5, kmax=100, verbose=True)

# ------------------------------------------------------------------------------
# Plotter
# ------------------------------------------------------------------------------

plotter = FormPlotter(form, figsize=(16, 9))

plotter.draw_nodes(radius=0.05, text="key")
plotter.draw_edges(text="force")
plotter.draw_loads(scale=0.5)
plotter.draw_residuals(scale=0.25)
plotter.draw_segments(edge_lines)

plotter.show()
