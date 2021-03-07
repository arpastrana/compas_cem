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
OPTIMIZE = 1

MODE = "autodiff"
# MODE = "numerical"

FIX_TO_PLANE = False
FIX_TO_LINE = True

# bounds - deviation edge variables
BOUND_D = 50.0
INCLUDE_TRAILS_AS_VARIABLES = False
BOUND_T = 0.1

# loads
P_LOAD = [0.0, 0.0, -1.0]

# target line rays
LINE_A = Line([-7, -5, -5], [-7, -5, 5])
LINE_B = Line([-7, 5, -5], [-7, 5, 5])

# optimization controls
OPT_ALGO = "LD_LBFGS"  # LN_BOBYQA / LD_LBFGS / LD_SLSQP
ITERS = 1000 # 1000
STOP_VAL = 1e-6 # 1e-6
STEP_SIZE = 1e-6  # 1e-6

# ------------------------------------------------------------------------------
# Form Diagram
# ------------------------------------------------------------------------------

form = FormDiagram()

# ------------------------------------------------------------------------------
# Add Nodes
# ------------------------------------------------------------------------------

form.add_node(Node(200,[-7, -5, 1]))
form.add_node(Node(201,[-6.455315, -4.18347, 1.082419]))
form.add_node(Node(202,[-5.985164, -3.320985, 1.15356]))
form.add_node(Node(203,[-5.607154, -2.413491, 1.210759]))
form.add_node(Node(204,[-5.340283, -1.466624, 1.25114]))
form.add_node(Node(205,[-5.201637, -0.492204, 1.27212]))
form.add_node(Node(206,[-5.201637, 0.492203, 1.27212]))
form.add_node(Node(207,[-5.340283, 1.466623, 1.25114]))
form.add_node(Node(208,[-5.607154, 2.413491, 1.210759]))
form.add_node(Node(209,[-5.985164, 3.320985, 1.15356]))
form.add_node(Node(210,[-6.455315, 4.18347, 1.082419]))
form.add_node(Node(211,[-7, 5, 1]))
form.add_node(Node(100,[-7, -5, 0]))
form.add_node(Node(101,[-6.455315, -4.18347, 0.082419]))
form.add_node(Node(102,[-5.985164, -3.320985, 0.15356]))
form.add_node(Node(103,[-5.607154, -2.413491, 0.210759]))
form.add_node(Node(104,[-5.340283, -1.466624, 0.25114]))
form.add_node(Node(105,[-5.201637, -0.492204, 0.27212]))
form.add_node(Node(106,[-5.201637, 0.492203, 0.27212]))
form.add_node(Node(107,[-5.340283, 1.466623, 0.25114]))
form.add_node(Node(108,[-5.607154, 2.413491, 0.210759]))
form.add_node(Node(109,[-5.985164, 3.320985, 0.15356]))
form.add_node(Node(110,[-6.455315, 4.18347, 0.082419]))
form.add_node(Node(111,[-7, 5, 0]))
form.add_node(Node(300,[-6.203173, -5.592055, 0.120572]))
form.add_node(Node(301,[-5.595776, -4.679409, 0.212481]))
form.add_node(Node(302,[-5.074039, -3.714226, 0.291427]))
form.add_node(Node(303,[-4.658055, -2.698023, 0.354372]))
form.add_node(Node(304,[-4.366766, -1.638476, 0.398449]))
form.add_node(Node(305,[-4.21407, -0.549749, 0.421554]))
form.add_node(Node(306,[-4.21407, 0.549749, 0.421554]))
form.add_node(Node(307,[-4.366766, 1.638476, 0.398449]))
form.add_node(Node(308,[-4.658055, 2.698023, 0.354372]))
form.add_node(Node(309,[-5.074039, 3.714226, 0.291427]))
form.add_node(Node(310,[-5.595776, 4.679409, 0.212481]))
form.add_node(Node(311,[-6.203173, 5.592055, 0.120572]))
form.add_node(Node(400,[-6.203173, -5.592055, 0.620572]))
form.add_node(Node(401,[-5.595776, -4.679409, 0.712481]))
form.add_node(Node(402,[-5.074039, -3.714226, 0.791427]))
form.add_node(Node(403,[-4.658055, -2.698023, 0.854372]))
form.add_node(Node(404,[-4.366766, -1.638476, 0.898449]))
form.add_node(Node(405,[-4.21407, -0.549749, 0.921554]))
form.add_node(Node(406,[-4.21407, 0.549749, 0.921554]))
form.add_node(Node(407,[-4.366766, 1.638476, 0.898449]))
form.add_node(Node(408,[-4.658055, 2.698023, 0.854372]))
form.add_node(Node(409,[-5.074039, 3.714226, 0.791427]))
form.add_node(Node(410,[-5.595776, 4.679409, 0.712481]))
form.add_node(Node(411,[-6.203173, 5.592055, 0.620572]))

# form.add_node(Node(200,[-7, -5, 1]))
# form.add_node(Node(201,[-5.415748, -1.786026, 1.239722]))
# form.add_node(Node(202,[-5.415748, 1.786026, 1.239722]))
# form.add_node(Node(203,[-7, 5, 1]))
# form.add_node(Node(100,[-7, -5, 0]))
# form.add_node(Node(101,[-5.415748, -1.786026, 0.239722]))
# form.add_node(Node(102,[-5.415748, 1.786026, 0.239722]))
# form.add_node(Node(103,[-7, 5, 0]))
# form.add_node(Node(300,[-6.203173, -5.592055, 0.120572]))
# form.add_node(Node(301,[-4.449149, -1.995681, 0.385983]))
# form.add_node(Node(302,[-4.449149, 1.995681, 0.385983]))
# form.add_node(Node(303,[-6.203173, 5.592055, 0.120572]))
# form.add_node(Node(400,[-6.203173, -5.592055, 0.620572]))
# form.add_node(Node(401,[-4.449149, -1.995681, 0.885983]))
# form.add_node(Node(402,[-4.449149, 1.995681, 0.885983]))
# form.add_node(Node(403,[-6.203173, 5.592055, 0.620572]))

# ------------------------------------------------------------------------------
# Compute number of bays
# ------------------------------------------------------------------------------

N_BAYS = max(list(form.nodes())) - 400 + 1

# ------------------------------------------------------------------------------
# Add Edges
# ------------------------------------------------------------------------------

form.add_edge(DeviationEdge(205,206,force=5))
form.add_edge(DeviationEdge(100,200,force=-0.1))
form.add_edge(DeviationEdge(101,201,force=-0.1))
form.add_edge(DeviationEdge(102,202,force=-0.1))
form.add_edge(DeviationEdge(103,203,force=-0.1))
form.add_edge(DeviationEdge(104,204,force=-0.1))
form.add_edge(DeviationEdge(105,205,force=-0.1))
form.add_edge(DeviationEdge(106,206,force=-0.1))
form.add_edge(DeviationEdge(107,207,force=-0.1))
form.add_edge(DeviationEdge(108,208,force=-0.1))
form.add_edge(DeviationEdge(109,209,force=-0.1))
form.add_edge(DeviationEdge(110,210,force=-0.1))
form.add_edge(DeviationEdge(111,211,force=-0.1))
form.add_edge(DeviationEdge(105,106,force=-5))
form.add_edge(TrailEdge(200,201,length=0.984985))
form.add_edge(TrailEdge(201,202,length=0.984877))
form.add_edge(TrailEdge(202,203,length=0.984738))
form.add_edge(TrailEdge(203,204,length=0.984585))
form.add_edge(TrailEdge(204,205,length=0.984458))
form.add_edge(TrailEdge(206,207,length=0.984586))
form.add_edge(TrailEdge(207,208,length=0.984738))
form.add_edge(TrailEdge(208,209,length=0.984877))
form.add_edge(TrailEdge(209,210,length=0.984985))
form.add_edge(TrailEdge(210,211,length=0.984985))
form.add_edge(TrailEdge(300,400,length=0.1))
form.add_edge(TrailEdge(301,401,length=0.1))
form.add_edge(TrailEdge(302,402,length=0.1))
form.add_edge(TrailEdge(303,403,length=0.1))
form.add_edge(TrailEdge(304,404,length=0.1))
form.add_edge(TrailEdge(305,405,length=0.1))
form.add_edge(TrailEdge(306,406,length=0.1))
form.add_edge(TrailEdge(307,407,length=0.1))
form.add_edge(TrailEdge(308,408,length=0.1))
form.add_edge(TrailEdge(309,409,length=0.1))
form.add_edge(TrailEdge(310,410,length=0.1))
form.add_edge(TrailEdge(311,411,length=0.1))
form.add_edge(DeviationEdge(100,300,force=-1.689))
form.add_edge(DeviationEdge(101,301,force=-1.689))
form.add_edge(DeviationEdge(102,302,force=-1.689))
form.add_edge(DeviationEdge(103,303,force=-1.689))
form.add_edge(DeviationEdge(104,304,force=-1.689))
form.add_edge(DeviationEdge(105,305,force=-1.689))
form.add_edge(DeviationEdge(106,306,force=-1.689))
form.add_edge(DeviationEdge(107,307,force=-1.689))
form.add_edge(DeviationEdge(108,308,force=-1.689))
form.add_edge(DeviationEdge(109,309,force=-1.689))
form.add_edge(DeviationEdge(110,310,force=-1.689))
form.add_edge(DeviationEdge(111,311,force=-1.689))
form.add_edge(DeviationEdge(200,300,force=1.689))
form.add_edge(DeviationEdge(201,301,force=1.689))
form.add_edge(DeviationEdge(202,302,force=1.689))
form.add_edge(DeviationEdge(203,303,force=1.689))
form.add_edge(DeviationEdge(204,304,force=1.689))
form.add_edge(DeviationEdge(205,305,force=1.689))
form.add_edge(DeviationEdge(206,306,force=1.689))
form.add_edge(DeviationEdge(207,307,force=1.689))
form.add_edge(DeviationEdge(208,308,force=1.689))
form.add_edge(DeviationEdge(209,309,force=1.689))
form.add_edge(DeviationEdge(210,310,force=1.689))
form.add_edge(DeviationEdge(211,311,force=1.689))
form.add_edge(TrailEdge(100,101,length=-0.984985))
form.add_edge(TrailEdge(101,102,length=-0.984877))
form.add_edge(TrailEdge(102,103,length=-0.984738))
form.add_edge(TrailEdge(103,104,length=-0.984585))
form.add_edge(TrailEdge(104,105,length=-0.984458))
form.add_edge(TrailEdge(106,107,length=-0.984586))
form.add_edge(TrailEdge(107,108,length=-0.984738))
form.add_edge(TrailEdge(108,109,length=-0.984877))
form.add_edge(TrailEdge(109,110,length=-0.984985))
form.add_edge(TrailEdge(110,111,length=-0.984985))

# form.add_edge(DeviationEdge(201,202,force=5))
# form.add_edge(DeviationEdge(100,200,force=-0.1))
# form.add_edge(DeviationEdge(101,201,force=-0.1))
# form.add_edge(DeviationEdge(102,202,force=-0.1))
# form.add_edge(DeviationEdge(103,203,force=-0.1))
# form.add_edge(DeviationEdge(101,102,force=-5))
# form.add_edge(TrailEdge(200,201,length=3.591233))
# form.add_edge(TrailEdge(202,203,length=3.591233))
# form.add_edge(TrailEdge(300,400,length=0.1))
# form.add_edge(TrailEdge(301,401,length=0.1))
# form.add_edge(TrailEdge(302,402,length=0.1))
# form.add_edge(TrailEdge(303,403,length=0.1))
# form.add_edge(DeviationEdge(100,300,force=-1.689))
# form.add_edge(DeviationEdge(101,301,force=-1.689))
# form.add_edge(DeviationEdge(102,302,force=-1.689))
# form.add_edge(DeviationEdge(103,303,force=-1.689))
# form.add_edge(DeviationEdge(200,300,force=1.689))
# form.add_edge(DeviationEdge(201,301,force=1.689))
# form.add_edge(DeviationEdge(202,302,force=1.689))
# form.add_edge(DeviationEdge(203,303,force=1.689))
# form.add_edge(TrailEdge(100,101,length=-3.591233))
# form.add_edge(TrailEdge(102,103,length=-3.591233))

# ------------------------------------------------------------------------------
# Add Supports
# ------------------------------------------------------------------------------

# first and last nodes in 100s and 200s series
for shift in (0, N_BAYS - 1):
    form.add_support(NodeSupport(int(100 + shift)))
    form.add_support(NodeSupport(int(200 + shift)))

# auxiliary trails supports - 400 series
for i in range(N_BAYS):
    form.add_support(NodeSupport(int(400 + i)))

# ------------------------------------------------------------------------------
# Add Loads
# ------------------------------------------------------------------------------

# loads go on the 300s series
for i in range(N_BAYS):
    form.add_load(NodeLoad(int(300 + i), P_LOAD))

# ------------------------------------------------------------------------------
# Force Equilibrium
# ------------------------------------------------------------------------------

force_equilibrium(form)

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

if INCLUDE_TRAILS_AS_VARIABLES:
    for edge in form.trail_edges():
        optimizer.add_constraint(TrailEdgeConstraint(edge, BOUND_T, BOUND_T))

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

    viewer.add(LINE_A)
    viewer.add(LINE_B)

    viewer.show()
