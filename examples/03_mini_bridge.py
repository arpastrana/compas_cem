import os
import matplotlib.pyplot as plt

from time import time

from compas_cem import JSON_DATA
from compas_cem import TEMP

from compas_cem.diagrams import TopologyDiagram

from compas_cem.loads import NodeLoad

from compas_cem.plotters import FormPlotter
from compas_cem.plotters import TopologyPlotter

from compas_cem.equilibrium import static_equilibrium

from compas_cem.optimization import Optimizer

from compas_cem.optimization import PointConstraint
from compas_cem.optimization import PlaneConstraint

from compas_cem.optimization import TrailEdgeParameter
from compas_cem.optimization import DeviationEdgeParameter

from compas.geometry import Plane
from compas.geometry import length_vector

# ------------------------------------------------------------------------------
# Data
#-------------------------------------------------------------------------------

IN = os.path.abspath(os.path.join(JSON_DATA, "w1_cem_2d_bridge_rhino.json"))

optimize = True
plot = True
view = False
save_fig = True

# ------------------------------------------------------------------------------
# Topology Diagram
# ------------------------------------------------------------------------------

topology = TopologyDiagram.from_json(IN)

# ------------------------------------------------------------------------------
# Store initial lines
# ------------------------------------------------------------------------------

keys = list(topology.deviation_edges())
deviation_force = 1.0
topology.edges_attribute(name="force", value=deviation_force, keys=keys)

load = [-1.0, 0.0, 0.0]
for node in topology.origin_nodes():
    topology.add_load(NodeLoad(node, load))

# ------------------------------------------------------------------------------
# Collect Edge lines
# ------------------------------------------------------------------------------

edge_lines = [topology.edge_coordinates(*edge) for edge in topology.edges()]

# ------------------------------------------------------------------------------
# Initialize optimizer
# ------------------------------------------------------------------------------

optimizer = Optimizer()

# ------------------------------------------------------------------------------
# Define constraints
# ------------------------------------------------------------------------------

optimizer.add_constraint(PointConstraint(node=7, point=[42.99, -14.17, 0.00]))
optimizer.add_constraint(PointConstraint(node=3, point=[29.13, 22.20, 0.00]))

# ------------------------------------------------------------------------------
# Define optimization parameters
# ------------------------------------------------------------------------------

bound_t = 20.0
bound_d = 20.0

for edge in topology.trail_edges():
    optimizer.add_parameter(TrailEdgeParameter(edge, bound_t, bound_t))

for edge in topology.deviation_edges():
    optimizer.add_parameter(DeviationEdgeParameter(edge, bound_d, bound_d))

# ------------------------------------------------------------------------------
# Generate trails
# ------------------------------------------------------------------------------

topology.build_trails()

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

if optimize:
    # record starting time
    start = time()

    # optimize
    form = optimizer.solve_nlopt(topology=topology,
                                 algorithm="LD_LBFGS",
                                 iters=100,
                                 eps=1e-6)

   # print out results
    print("Form. # Nodes: {}, # Edges: {}".format(form.number_of_nodes(),
                                                  form.number_of_edges()))
    print("Optimizer. # Parameters {}, # Constraints {}".format(optimizer.number_of_parameters(),
                                                         optimizer.number_of_constraints()))
    print("Elapsed time: {}".format(time() - start))
    print("Total error: {}".format(optimizer.penalty))

# ------------------------------------------------------------------------------
# Print put residual forces at supports (a.k.a reaction forces)
# ------------------------------------------------------------------------------

    for node in form.support_nodes():
        reaction_force = form.reaction_force(node)
        print("node: {} reaction force: {}".format(node, reaction_force))

# ------------------------------------------------------------------------------
# Plotter
# ------------------------------------------------------------------------------

if plot:
    plotter = FormPlotter(form, figsize=(16, 9))

    plotter.draw_nodes(radius=0.30)
    plotter.draw_edges()
    plotter.draw_loads(scale=2.0, gap=0.75)
    plotter.draw_reactions(scale=2.0, gap=0.75)
    plotter.draw_segments(edge_lines)

    points = []
    for key, constraint in optimizer.constraints.items():
        if not isinstance(constraint, PointConstraint):
            continue
        pt = constraint.target()
        points.append({
            "pos": pt[:2],
            "radius": 0.5,
            "facecolor": (255, 153, 0)
        })

    plotter.draw_points(points)

    if save_fig:
        path = os.path.abspath(os.path.join(TEMP, "iass_2021/mini_bridge"))
        plt.autoscale()
        plt.tight_layout()
        plt.savefig(path, bbox_inches='tight', pad_inches=0)

    plotter.show()
