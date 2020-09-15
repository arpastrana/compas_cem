import os

from compas_cem import JSON_DATA

from compas_cem.diagrams import FormDiagram
from compas_cem.plotters import FormPlotter
from compas_cem.viewers import FormViewer

# ------------------------------------------------------------------------------
# Data
#-------------------------------------------------------------------------------

IN = os.path.abspath(os.path.join(JSON_DATA, "w1_cem_2d_bridge_rhino.json"))

plot = True
view = True

# ------------------------------------------------------------------------------
# Form Diagram
# ------------------------------------------------------------------------------

form = FormDiagram.from_json(IN)

# ------------------------------------------------------------------------------
# Plotter
# ------------------------------------------------------------------------------

if plot:

    plotter = FormPlotter(form, figsize=(16, 9))
    plotter.draw_nodes(radius=0.30, text="key")
    plotter.draw_edges(text="force")
    plotter.draw_loads(scale=-2.0)
    plotter.draw_residuals(scale=-0.25)

    plotter.show()

# ------------------------------------------------------------------------------
# Viewer
# ------------------------------------------------------------------------------

if view:

    viewer = FormViewer(form)
    viewer.add_nodes(size=20)
    viewer.add_edges(width=(1, 5))
    viewer.add_loads(scale=-2, width=15)
    viewer.add_residuals(scale=-0.25, width=15)

    viewer.show()
