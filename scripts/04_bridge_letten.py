import os

from math import fabs

from compas_cem import JSON_DATA

from compas_cem.diagrams import FormDiagram
from compas_cem.viewers import FormViewer

from compas.geometry import Point
from compas.geometry import Frame
from compas.geometry import Transformation
from compas.geometry import centroid_points

# ------------------------------------------------------------------------------
# Data
#-------------------------------------------------------------------------------

IN = os.path.abspath(os.path.join(JSON_DATA, "w2_cem_3d_bridge_rhino.json"))

plot = False
view = True

# ------------------------------------------------------------------------------
# Form Diagram
# ------------------------------------------------------------------------------

form = FormDiagram.from_json(IN)

# ------------------------------------------------------------------------------
# Relocate form
# ------------------------------------------------------------------------------

base_f = Frame.worldXY()
base_f.point = centroid_points([form.node_xyz(node) for node in form.nodes()])
T = Transformation.from_frame_to_frame(base_f, Frame.worldXY())

for node in form.nodes():
    x, y, z = form.node_xyz(node)
    xyz = Point(x, y, z).transformed(T)
    form.node_xyz(node, xyz)

# ------------------------------------------------------------------------------
# Prepare keys
# ------------------------------------------------------------------------------

ekeys = [edge for edge in form.edges() if fabs(form.edge_force(edge)) > 0.0]
nkeys = [node for edge in ekeys for node in edge]

# ------------------------------------------------------------------------------
# Viewer
# ------------------------------------------------------------------------------

if view:

    viewer = FormViewer(form)
    viewer.add_nodes(keys=nkeys, size=20)
    viewer.add_edges(keys=ekeys, width=(1, 5))
    viewer.add_residuals(keys=nkeys, scale=0.5, width=5)
    viewer.add_loads(scale=5, width=5)

    viewer.show()
