import os
from compas_cem import JSON_DATA
from compas_cem.diagrams import FormDiagram
from compas_cem.plotters import FormPlotter

IN = os.path.abspath(os.path.join(JSON_DATA, "w1_cem_2d_bridge_rhino.json"))
form = FormDiagram.from_json(IN)

plotter = FormPlotter(form, figsize=(8, 4.5))
plotter.draw_nodes(radius=0.30, text="key")
plotter.draw_edges(text="force")
plotter.draw_loads(scale=-2.0)
plotter.draw_residuals(scale=-0.25)

plotter.show()