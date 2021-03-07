import os

from time import time
from math import fabs

from compas.geometry import length_vector
from compas.geometry import Vector
from compas.geometry import Plane
from compas.geometry import Line

from compas_cem import JSON_DATA
from compas_cem import TEMP

from compas_cem.diagrams import FormDiagram

from compas_cem.elements import Node
from compas_cem.elements import DeviationEdge
from compas_cem.elements import TrailEdge

from compas_cem.supports import NodeSupport

from compas_cem.loads import NodeLoad

from compas_cem.viewers import FormViewer

from compas_cem.equilibrium import force_equilibrium

from compas_cem.optimization import Optimizer

from compas_cem.optimization import NodeResidualGoal
from compas_cem.optimization import LineGoal
from compas_cem.optimization import PlaneGoal

from compas_cem.optimization import TrailEdgeConstraint
from compas_cem.optimization import DeviationEdgeConstraint


# ------------------------------------------------------------------------------
# Data
# ------------------------------------------------------------------------------

VIEW = True
OPTIMIZE = 0

MODE = "autodiff"
# MODE = "numerical"

FIX_TO_PLANE = False
FIX_TO_LINE = False

# bounds - deviation edge variables
BOUND_D = 50.0

# optimization controls
OPT_ALGO = "LD_LBFGS"  # LN_BOBYQA / LD_LBFGS / LD_SLSQP
ITERS = 1000 # 1000
STOP_VAL = 1e-6 # 1e-6
STEP_SIZE = 1e-6  # 1e-6

JSON_IN = os.path.abspath("/Users/arpj/princeton_docs/phd/paper_notes/papers/cem_autograd/Tree/tree.json")
# ------------------------------------------------------------------------------
# Form Diagram
# ------------------------------------------------------------------------------

form = FormDiagram.from_json(JSON_IN)

# ------------------------------------------------------------------------------
# Force Equilibrium
# ------------------------------------------------------------------------------

# force_equilibrium(form)

# ------------------------------------------------------------------------------
# Initialize optimizer
# ------------------------------------------------------------------------------

optimizer = Optimizer()

# ------------------------------------------------------------------------------
# Define goals / Targets
# ------------------------------------------------------------------------------

if FIX_TO_PLANE:
    # Cross-section bays should stay on a plane - all nodes in the 100s, 200s, 300s
    for i in range(N_BAYS):
        # make a plane

        bay = [int(key + i) for key in (100, 200, 300)]
        a, b, c = [form.node_coordinates(node) for node in bay]
        plane = Plane.from_three_points(a, b, c)

        # assign it to nodes in series 100s, 200s, 300s
        for node in bay:
            optimizer.add_goal(PlaneGoal(node, plane))

# Minimize residuals in auxiliary trails - all nodes in the 400s series
for node in form.nodes():
    if node >= 400:
        optimizer.add_goal(NodeResidualGoal(node, [0.0, 0.0, 0.0]))

if FIX_TO_LINE:
    # Supports should stay on a line ray - series 100s and 200s
    for shift, line in zip((0, N_BAYS - 1), (LINE_A, LINE_B)):
        # first and start nodes of the series
        optimizer.add_goal(LineGoal(int(100 + shift), line))
        optimizer.add_goal(LineGoal(int(200 + shift), line))

# ------------------------------------------------------------------------------
# Define optimization parameters / constraints
# ------------------------------------------------------------------------------

for edge in form.deviation_edges():
    optimizer.add_constraint(DeviationEdgeConstraint(edge, BOUND_D, BOUND_D))


# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

if OPTIMIZE:
    # record starting time
    start = time()

    # optimize
    x_opt, l_opt = optimizer.solve_nlopt(form=form,
                                         algorithm=OPT_ALGO,
                                         iters=ITERS,
                                         step_size=STEP_SIZE,
                                         stopval=STOP_VAL,
                                         ftol=None,
                                         mode=MODE,
                                         verbose=False)

   # print out results
    print("Form. # Nodes: {}, # Edges: {}".format(form.number_of_nodes(), form.number_of_edges()))
    print("Optimizer. # Variables {}, # Goals {}".format(optimizer.number_of_constraints(), optimizer.number_of_goals()))
    print("Elapsed time: {}".format(time() - start))
    print("Total error: {}".format(l_opt))

# ------------------------------------------------------------------------------
# Print put residual forces at supports (a.k.a reaction forces)
# ------------------------------------------------------------------------------

    for node in form.support_nodes():
        if node < 400:
            continue
        residual = length_vector(form.node_residual(node))
        print("node: {} reaction force: {}".format(node, residual))

# ------------------------------------------------------------------------------
# Viewer
# ------------------------------------------------------------------------------

if VIEW:

    viewer = FormViewer(form)

    viewer.add_nodes(size=20)
    viewer.add_edges(width=(1, 5))
    viewer.add_residuals(scale=1.0, width=2)
    viewer.add_loads(scale=1, width=2)


    viewer.show()
