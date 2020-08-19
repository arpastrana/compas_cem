from compas_cem.diagrams import TopologyDiagram
from compas_cem.plotters import TopologyPlotter

from compas_cem.equilibrium import force_equilibrium

# ------------------------------------------------------------------------------
# Data
#-------------------------------------------------------------------------------

IN = "/Users/arpj/code/libraries/compas_cem/data/json/3d_test.json"

# ------------------------------------------------------------------------------
# Topology Diagram
# ------------------------------------------------------------------------------

topology = TopologyDiagram.from_json(IN)

# ------------------------------------------------------------------------------
# Collect Trails and Edge lines
# ------------------------------------------------------------------------------

tr = topology.trails()
edge_lines = [topology.edge_coordinates(*edge) for edge in topology.edges()]

# ------------------------------------------------------------------------------
# Force Equilibrium
# ------------------------------------------------------------------------------

force_equilibrium(topology, kmax=100, verbose=True)

# ------------------------------------------------------------------------------
# Visualization
# ------------------------------------------------------------------------------

from compas.utilities import geometric_key
from compas.datastructures import network_transformed
from compas.geometry import Rotation
from math import radians

edge_text = None
# node_text = None
# edge_text = {e: round(attr["state"] * attr["force"], 6) for e, attr in topology.edges(True)}
# edge_text = {e: attr["type"] for e, attr in topology.edges(True)}
node_text = {n: geometric_key(topology.node_coordinates(n), precision="3f") for n in topology.nodes()}

transformation = Rotation.from_axis_and_angle([1, 0, 0], radians(-90))
topology = network_transformed(topology, transformation)


plotter = TopologyPlotter(topology, figsize=(16, 9))

plotter.draw_nodes(radius=0.03, text=node_text)
plotter.draw_edges(text=edge_text)
plotter.draw_loads()
# plotter.draw_segments(edge_lines)

plotter.show()
