import os
import numpy as np
import matplotlib.pyplot as plt

from time import time
from math import pi
from math import cos
from math import sin

from compas.utilities import pairwise

from compas_cem import TEMP

from compas_cem.diagrams import FormDiagram

from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.elements import DeviationEdge

from compas_cem.supports import NodeSupport

from compas_cem.equilibrium import force_equilibrium

from compas_cem.optimization import Optimizer
from compas_cem.optimization import TrailEdgeForceGoal
from compas_cem.optimization import NodeResidualGoal
from compas_cem.optimization import DeviationEdgeConstraint

from compas_cem.plotters import FormPlotter


diameter = 1.0
num_steps = 256 # only even numbers
appendix_length = 0.10
force = 1.0
tension_force = +force
compression_force = -force
bound = 2.0
grad_mode = "autodiff"

plot_text_nodes = False
plot_text_edges = False
save_fig = True

# ------------------------------------------------------------------------------
# Form Diagram
# ------------------------------------------------------------------------------

assert num_steps % 2 == 0

# create a form diagram
form = FormDiagram()

# create nodes, removing last
thetas = np.linspace(0.0, 2*pi, num_steps + 1)[:-1]
radius = diameter / 2.0

for i, theta in enumerate(thetas):

    x = radius * cos(theta)
    y = radius * sin(theta)

    # nodes in the wheel
    form.add_node(Node(i, [x, y, 0.0]))

    # nodes outside of the wheel are supported
    j = int(i + num_steps)
    form.add_node(Node(j, [x, y + appendix_length, 0.0]))
    form.add_support(NodeSupport(j))

    # trail edges connecting internal and external wheel nodes
    form.add_edge(TrailEdge(i, j, length=appendix_length))


# deviation edges in tension
for u, v in pairwise(list(range(num_steps)) + [0]):
    form.add_edge(DeviationEdge(u, v, force=tension_force))


# deviation edges in compression
half_num_steps = num_steps / 2.0

for u in range(int(half_num_steps)):

    v = int(u + half_num_steps)
    form.add_edge(DeviationEdge(u, v, force=compression_force))

# assert total number of edges is correct
assert form.number_of_edges() == num_steps * 2 + half_num_steps

# ------------------------------------------------------------------------------
# Force equilibrium
# ------------------------------------------------------------------------------

force_equilibrium(form, eps=1e-5, kmax=100)

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

# create optimizer
optimizer = Optimizer()

# add goals
# for edge in form.trail_edges():
#     optimizer.add_goal(TrailEdgeForceGoal(edge, force=0.0))

for node in form.support_nodes():
    optimizer.add_goal(NodeResidualGoal(node, residual_vector=[0.0, 0.0, 0.0]))

# add optimization variables
for edge in form.deviation_edges():
    # compression bounds
    low_bound, up_bound = (bound, force)

    # tension bounds
    if form.edge_force(edge) > 0.0:
        low_bound, up_bound = (force, bound)

    optimizer.add_constraint(DeviationEdgeConstraint(edge, low_bound, up_bound))

# optimize
start = time()

# optimization constants
opt_algorithm = "LD_LBFGS"  # LN_BOBYQA / LD_LBFGS / LD_SLSQP
iters = 1000  # 100
stopval = 1e-6  # 1e-4
step_size = 1e-6  # 1e-4

# optimize
x_opt, l_opt = optimizer.solve_nlopt(form,
                                     opt_algorithm,
                                     iters,
                                     stopval,
                                     step_size,
                                     mode=grad_mode,
                                     verbose=False)

# print out results
print("Form. # Nodes: {}, # Edges: {}".format(form.number_of_nodes(),
                                              form.number_of_edges()))
print("Optimizer. # Variables {}, # Goals {}".format(optimizer.number_of_constraints(),
                                                     optimizer.number_of_goals()))
print("Elapsed time: {}".format(time() - start))
print("Total error: {}".format(l_opt))


# ------------------------------------------------------------------------------
# Plot
# ------------------------------------------------------------------------------

plotter = FormPlotter(form, figsize=(16, 9))

text_nodes = None
text_edges = None
if plot_text_nodes:
    text_nodes = "key-xyz"
if plot_text_edges:
    text_edges = "force-length"


keys = list(form.root_nodes())
plotter.draw_nodes(radius=0.001, keys=keys, text=text_nodes)

keys = list(form.deviation_edges())
plotter.draw_edges(text=text_edges, keys=keys)

plotter.draw_loads(scale=-0.1)
plotter.draw_residuals(scale=-0.10)

if save_fig:
    path = os.path.abspath(os.path.join(TEMP, f"iass_2021/wheel_{num_steps}sides"))
    plt.autoscale()
    plt.tight_layout()
    plt.savefig(path, bbox_inches='tight', pad_inches=0)

plotter.show()
