from time import time
from math import pi
from math import cos
from math import sin
from math import fabs

import numpy as np

from compas.utilities import pairwise

from compas_cem.diagrams import TopologyDiagram

from compas_cem.elements import Node
from compas_cem.elements import DeviationEdge

from compas_cem.equilibrium import static_equilibrium

from compas_cem.optimization import Optimizer

from compas_cem.optimization import TrailEdgeForceConstraint
from compas_cem.optimization import DeviationEdgeParameter

from compas_plotters import Plotter
# from compas_cem.plotters import FormPlotter
# from compas_cem.plotters import TopologyPlotter


diameter = 1.0
num_steps = 24  # only even numbers
appendix_length = 0.10
force = 1.0
tension_force = +force
compression_force = -force
bound = 2.0

plot_text_nodes = False
plot_text_edges = False

# ------------------------------------------------------------------------------
# Topology Diagram
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

# deviation edges in the perimeter of the wheel tension
for u, v in pairwise(list(range(num_steps)) + [0]):
    topology.add_edge(DeviationEdge(u, v, force=tension_force))

# internal deviation edges are in compression
half_num_steps = num_steps / 2.0

for u in range(int(half_num_steps)):
    v = int(u + half_num_steps)
    topology.add_edge(DeviationEdge(u, v, force=compression_force))

# ------------------------------------------------------------------------------
# Generate trails and auxiliary trails
# ------------------------------------------------------------------------------

topology.auxiliary_trail_length = appendix_length
topology.build_trails(auxiliary_trails=True)

# ------------------------------------------------------------------------------
# Equilibrate internal forces
# ------------------------------------------------------------------------------

form = static_equilibrium(topology, eta=1e-6, tmax=100)

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

# create optimizer
optimizer = Optimizer()

# add constraints
for edge in topology.auxiliary_trail_edges():
    optimizer.add_constraint(TrailEdgeForceConstraint(edge, force=0.0))

# add optimization parameters
# the forces in all the deviation edges are allowed to fluctuate
for edge in topology.deviation_edges():
    # compression bounds
    low_bound, up_bound = (bound, force)
    # tension bounds
    if topology.edge_force(edge) > 0.0:
        low_bound, up_bound = (force, bound)

    optimizer.add_parameter(DeviationEdgeParameter(edge, low_bound, up_bound))

# optimize
start = time()
form = optimizer.solve_nlopt(topology, algorithm="LBFGS", iters=1000, eps=1e-6)

# print out results
print("Topology. # Nodes: {}, # Edges: {}".format(topology.number_of_nodes(),
                                                  topology.number_of_edges()))
print("Optimizer. # Parameters {}, # Constraints {}".format(optimizer.number_of_parameters(),
                                                            optimizer.number_of_constraints()))
print("Elapsed time: {}".format(time() - start))

# the following values should be lower or equal to eps
print("Value of the objective function: {}".format(optimizer.penalty))
print("Norm of the gradient of the objective function: {}".format(optimizer.gradient_norm))


# ------------------------------------------------------------------------------
# Plot topology
# ------------------------------------------------------------------------------

plotter = Plotter()
plotter.add(topology, nodesize=0.4)
plotter.zoom_extents()
plotter.show()

# plotter = TopologyPlotter(topology, figsize=(16, 9))

# plotter.draw_loads(radius=0.01)
# plotter.draw_nodes(radius=0.01)
# plotter.draw_edges()

# plotter.show()

# ------------------------------------------------------------------------------
# Plot Form
# ------------------------------------------------------------------------------

plotter = Plotter()
plotter.add(form, nodesize=0.4)
plotter.zoom_extents()
plotter.show()

# plotter = FormPlotter(form, figsize=(16, 9))

# keys = list(topology.origin_nodes())
# plotter.draw_nodes(radius=0.01, keys=keys)

# # plot only edges with a force larger than 0.001
# keys = [edge for edge in form.edges() if fabs(form.edge_force(edge)) > 0.001]
# plotter.draw_edges(keys=keys)
# plotter.draw_loads(scale=0.1)
# plotter.draw_reactions(scale=0.10)

# plotter.show()
