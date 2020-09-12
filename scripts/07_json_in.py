from compas_cem.diagrams import TopologyDiagram
from compas_cem.plotters import TopologyPlotter
from compas_cem.viewers import TopologyViewer

# ------------------------------------------------------------------------------
# Data
#-------------------------------------------------------------------------------

IN = "/Users/arpj/code/libraries/compas_cem/data/json/w1_cem_2d_bridge_rhino.json"

plot = True
view = False

# ------------------------------------------------------------------------------
# Topology Diagram
# ------------------------------------------------------------------------------

topology = TopologyDiagram.from_json(IN)

# ------------------------------------------------------------------------------
# Plotter
# ------------------------------------------------------------------------------

if plot:

    plotter = TopologyPlotter(topology, figsize=(16, 9))

    plotter.draw_nodes(radius=0.30, text="key")
    plotter.draw_edges(text="force")
    plotter.draw_loads(scale=-2.0)
    plotter.draw_residuals(scale=-0.25)

    plotter.show()

# ------------------------------------------------------------------------------
# Viewer
# ------------------------------------------------------------------------------

if view:

    viewer = TopologyViewer(topology)
    viewer.add_nodes(size=20)
    viewer.add_edges(width=(1, 5))
    viewer.add_loads(scale=-2, width=15)
    viewer.add_residuals(scale=-0.25, width=15)

    viewer.show()
