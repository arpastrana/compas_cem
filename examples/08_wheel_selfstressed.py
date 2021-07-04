import os

from time import time
from math import pi
from math import cos
from math import sin

import numpy as np
import matplotlib.pyplot as plt

from compas.utilities import pairwise

from compas_cem import TEMP

from compas_cem.diagrams import TopologyDiagram

from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.elements import DeviationEdge

from compas_cem.supports import NodeSupport

from compas_cem.equilibrium import static_equilibrium

from compas_cem.optimization import Optimizer

from compas_cem.optimization import TrailEdgeForceConstraint
from compas_cem.optimization import ReactionForceConstraint
from compas_cem.optimization import DeviationEdgeParameter

from compas_cem.plotters import FormPlotter
from compas_cem.plotters import TopologyPlotter


diameter = 1.0
num_steps = 8 # only even numbers
appendix_length = 0.10
force = 1.0
tension_force = +force
compression_force = -force
bound = 2.0

plot_text_nodes = False
plot_text_edges = False
save_fig = True

# ------------------------------------------------------------------------------
# Form Diagram
# ------------------------------------------------------------------------------

assert num_steps % 2 == 0

# create a topology diagram
topology = TopologyDiagram()

# create nodes, removing last
thetas = np.linspace(0.0, 2*pi, num_steps + 1)[:-1]
radius = diameter / 2.0

for i, theta in enumerate(thetas):

    x = radius * cos(theta)
    y = radius * sin(theta)

    # nodes in the wheel
    topology.add_node(Node(i, [x, y, 0.0]))

    # nodes outside of the wheel are supported
    j = int(i + num_steps)
    topology.add_node(Node(j, [x, y + appendix_length, 0.0]))
    topology.add_support(NodeSupport(j))

    # trail edges connecting internal and external wheel nodes
    topology.add_edge(TrailEdge(i, j, length=appendix_length))


# deviation edges in tension
for u, v in pairwise(list(range(num_steps)) + [0]):
    topology.add_edge(DeviationEdge(u, v, force=tension_force))


# deviation edges in compression
half_num_steps = num_steps / 2.0

for u in range(int(half_num_steps)):

    v = int(u + half_num_steps)
    topology.add_edge(DeviationEdge(u, v, force=compression_force))

# assert total number of edges is correct
assert topology.number_of_edges() == num_steps * 2 + half_num_steps

# ------------------------------------------------------------------------------
# Generate trails
# ------------------------------------------------------------------------------

topology.build_trails()

# ------------------------------------------------------------------------------
# Equilibrate internal forces
# ------------------------------------------------------------------------------

form = static_equilibrium(topology, eta=1e-5, tmax=100)

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

# create optimizer
optimizer = Optimizer()

# add constraints
for node in topology.support_nodes():
    optimizer.add_constraint(ReactionForceConstraint(node, vector=[0.0, 0.0, 0.0]))

# add optimization variables
for edge in topology.deviation_edges():
    # compression bounds
    low_bound, up_bound = (bound, force)

    # tension bounds
    if topology.edge_force(edge) > 0.0:
        low_bound, up_bound = (force, bound)

    optimizer.add_parameter(DeviationEdgeParameter(edge, low_bound, up_bound))

# optimize
start = time()

# optimize
form = optimizer.solve_nlopt(topology,
                             algorithm="LD_LBFGS",
                             iters=1000,
                             eps=1e-6)

# print out results
print("Topology. # Nodes: {}, # Edges: {}".format(topology.number_of_nodes(),
                                              topology.number_of_edges()))
print("Optimizer. # Parameters {}, # Constraints {}".format(optimizer.number_of_parameters(),
                                                     optimizer.number_of_constraints()))
print("Elapsed time: {}".format(time() - start))
print("Total error: {}".format(optimizer.penalty))

# ------------------------------------------------------------------------------
# Plot topology
# ------------------------------------------------------------------------------

plotter = TopologyPlotter(topology, figsize=(16, 9))

plotter.draw_loads(radius=0.025)
plotter.draw_nodes(radius=0.025)
plotter.draw_edges()

plotter.show()

# ------------------------------------------------------------------------------
# Plot Form
# ------------------------------------------------------------------------------

plotter = FormPlotter(form, figsize=(16, 9))

text_nodes = None
text_edges = None
if plot_text_nodes:
    text_nodes = "key-xyz"
if plot_text_edges:
    text_edges = "force-length"


keys = list(topology.origin_nodes())
plotter.draw_nodes(radius=0.001, keys=keys, text=text_nodes)

keys = list(topology.deviation_edges())
plotter.draw_edges(text=text_edges, keys=keys)
plotter.draw_loads(scale=0.1)
plotter.draw_reactions(scale=0.10)

if save_fig:
    path = os.path.abspath(os.path.join(TEMP, f"iass_2021/wheel_{num_steps}sides"))
    plt.autoscale()
    plt.tight_layout()
    plt.savefig(path, bbox_inches='tight', pad_inches=0)

plotter.show()
