import os

from time import time

from compas_cem import JSON_DATA

from compas_cem.diagrams import FormDiagram

from compas_cem.loads import NodeLoad

from compas_cem.plotters import FormPlotter
from compas_cem.viewers import FormViewer

from compas_cem.equilibrium import force_equilibrium

from compas_cem.optimization import Optimizer

from compas_cem.optimization import PointGoal
from compas_cem.optimization import PlaneGoal

from compas_cem.optimization import TrailEdgeConstraint
from compas_cem.optimization import DeviationEdgeConstraint

from compas.geometry import Plane
from compas.geometry import length_vector

# ------------------------------------------------------------------------------
# Data
#-------------------------------------------------------------------------------

IN = os.path.abspath(os.path.join(JSON_DATA, "w1_cem_2d_bridge_rhino.json"))

optimize = True
plot = True
view = True

# ------------------------------------------------------------------------------
# Form Diagram
# ------------------------------------------------------------------------------

form = FormDiagram.from_json(IN)

# ------------------------------------------------------------------------------
# Store initial lines
# ------------------------------------------------------------------------------

keys = list(form.deviation_edges())
deviation_force = 1.0
form.edges_attribute(name="force", value=deviation_force, keys=keys)

load = [-2.0, 0.0, 0.0]
for node in form.root_nodes():
    form.add_load(NodeLoad(node, load))

# ------------------------------------------------------------------------------
# Collect Trails and Edge lines
# ------------------------------------------------------------------------------

tr = form.trails()
edge_lines = [form.edge_coordinates(*edge) for edge in form.edges()]

# ------------------------------------------------------------------------------
# Initialize optimizer
# ------------------------------------------------------------------------------

optimizer = Optimizer()

# ------------------------------------------------------------------------------
# Define goals / Targets
# ------------------------------------------------------------------------------

optimizer.add_goal(PointGoal(node=3, point=[29.13,22.20,0.00]))
optimizer.add_goal(PointGoal(node=7, point=[42.99,-14.17,0.00]))

# ------------------------------------------------------------------------------
# Define optimization parameters / constraints
# ------------------------------------------------------------------------------

bound_t = 20.0
bound_d = 20.0

for edge in form.trail_edges():
    optimizer.add_constraint(TrailEdgeConstraint(edge, bound_t, bound_t))

for edge in form.deviation_edges():
    optimizer.add_constraint(DeviationEdgeConstraint(edge, bound_d, bound_d))
        
# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

if optimize:
    # record starting time
    start = time()

    # optimization constants
    opt_algorithm = "LD_LBFGS"  # LN_BOBYQA / LD_LBFGS
    iters = 100  # 100
    stopval = 1e-4  # 1e-4
    step_size = 1e-6  # 1e-4

    # optimize
    x_opt, l_opt = optimizer.solve_nlopt(form, opt_algorithm, iters, stopval, step_size)

    # print out results
    print("Elapsed time: {}".format(time() - start))
    print("Total error: {}".format(l_opt))

# ------------------------------------------------------------------------------
# Print put residual forces at supports (a.k.a reaction forces)
# ------------------------------------------------------------------------------

    for node in form.support_nodes():
        residual = length_vector(form.node_residual(node))
        print("node: {} residual: {}".format(node, residual))

# ------------------------------------------------------------------------------
# Plotter
# ------------------------------------------------------------------------------

if plot:
    plotter = FormPlotter(form, figsize=(16, 9))

    plotter.draw_nodes(radius=0.30, text="key")
    plotter.draw_edges(text="force")
    plotter.draw_loads(scale=-2.0)
    plotter.draw_residuals(scale=-0.25)
    plotter.draw_segments(edge_lines)

    points = []
    for key, goal in optimizer.goals.items():
        if not isinstance(goal, PointGoal):
            continue
        pt = goal.target_geometry()
        points.append({
            "pos": pt[:2],
            "radius": 0.5,
            "facecolor": (255, 153, 0)
        }
        )

    plotter.draw_points(points)

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

    points = []
    for key, goal in optimizer.goals.items():
        if not isinstance(goal, PointGoal):
            continue
        points.append(goal.target_geometry())

    viewer.add_points(points, size=30)

    viewer.show()
