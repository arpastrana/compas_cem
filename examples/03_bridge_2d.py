import os

from time import time

from compas_cem.diagrams import TopologyDiagram

from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport

from compas_cem.plotters import FormPlotter

from compas_cem.equilibrium import static_equilibrium

from compas_cem.optimization import Optimizer

from compas_cem.optimization import PointConstraint

from compas_cem.optimization import TrailEdgeParameter
from compas_cem.optimization import DeviationEdgeParameter


# ------------------------------------------------------------------------------
# Data
#-------------------------------------------------------------------------------

HERE = os.path.dirname(__file__)
IN = os.path.abspath(os.path.join(HERE, "03_bridge_2d.json"))
optimize = True

# ------------------------------------------------------------------------------
# Topology Diagram
# ------------------------------------------------------------------------------

topology = TopologyDiagram.from_json(IN)

# ------------------------------------------------------------------------------
# Add supports
# ------------------------------------------------------------------------------

topology.add_support(NodeSupport(1))
topology.add_support(NodeSupport(5))

# ------------------------------------------------------------------------------
# Apply loads
# ------------------------------------------------------------------------------

load = [0.0, -1.0, 0.0]
topology.add_load(NodeLoad(2, load))
topology.add_load(NodeLoad(6, load))

# ------------------------------------------------------------------------------
# Generate trails
# ------------------------------------------------------------------------------

topology.build_trails()

# ------------------------------------------------------------------------------
# Form-finding
# ------------------------------------------------------------------------------

form = static_equilibrium(topology)

# ------------------------------------------------------------------------------
# Collect form edge lines
# ------------------------------------------------------------------------------

form_lines = [form.edge_coordinates(*edge) for edge in form.edges()]

# ------------------------------------------------------------------------------
# Initialize optimizer
# ------------------------------------------------------------------------------

if optimize:
    optimizer = Optimizer()

# ------------------------------------------------------------------------------
# Define constraints
# ------------------------------------------------------------------------------

    optimizer.add_constraint(PointConstraint(node=1, point=[-20.67, 42.7, 0.0]))
    optimizer.add_constraint(PointConstraint(node=5, point=[15.7, 28.84, 0.0]))

# ------------------------------------------------------------------------------
# Define optimization parameters
# ------------------------------------------------------------------------------

    bound_t = 15.0
    bound_d = 10.0

    for edge in topology.trail_edges():
        optimizer.add_parameter(TrailEdgeParameter(edge, bound_t, bound_t))

    for edge in topology.deviation_edges():
        optimizer.add_parameter(DeviationEdgeParameter(edge, bound_d, bound_d))

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

    # record starting time
    start = time()

    # optimize
    form = optimizer.solve_nlopt(topology=topology, algorithm="LD_SLSQP", iters=100, eps=1e-6)

   # print out results
    print("Form. # Nodes: {}, # Edges: {}".format(form.number_of_nodes(),
                                                  form.number_of_edges()))
    print("Optimizer. # Parameters {}, # Constraints {}".format(optimizer.number_of_parameters(),
                                                                optimizer.number_of_constraints()))
    print("Elapsed time: {}".format(time() - start))
    print("Total penalty: {}".format(optimizer.penalty))

# ------------------------------------------------------------------------------
# Print put residual forces at supports (a.k.a reaction forces)
# ------------------------------------------------------------------------------

    for node in form.support_nodes():
        reaction_force = form.reaction_force(node)
        print("node: {} reaction force: {}".format(node, reaction_force))

# ------------------------------------------------------------------------------
# Plotter
# ------------------------------------------------------------------------------

plotter = FormPlotter(form, figsize=(16, 9))

plotter.draw_nodes(radius=0.30, text="key")
plotter.draw_edges()
plotter.draw_loads(scale=2.0, gap=0.75)
plotter.draw_reactions(scale=2.0, gap=0.75)

if optimize:
    plotter.draw_segments(form_lines)

    points = []
    for key, constraint in optimizer.constraints.items():
        if not isinstance(constraint, PointConstraint):
            continue
        pt = constraint.target()
        points.append({"pos": pt[:2], "radius": 0.5, "facecolor": (255, 153, 0)})

    plotter.draw_points(points)

plotter.show()
