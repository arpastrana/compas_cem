from time import time
from math import pi
from math import cos
from math import sin

import numpy as np

from compas.geometry import Translation

from compas.utilities import pairwise

from compas_cem.diagrams import TopologyDiagram

from compas_cem.elements import Node
from compas_cem.elements import DeviationEdge

from compas_cem.equilibrium import static_equilibrium

from compas_cem.optimization import Optimizer

from compas_cem.optimization import TrailEdgeForceConstraint
from compas_cem.optimization import DeviationEdgeParameter

from compas_cem.plotters import Plotter


# ------------------------------------------------------------------------------
# Create a topology diagram
# ------------------------------------------------------------------------------

# geometry parameters
diameter = 1.0
num_sides = 16  # only even numbers
appendix_length = 0.10
tension_force = 1.0
compression_force = -0.5
bound = 2.0

# test number of subdivisions is even
assert num_sides % 2 == 0

# create a topology diagram
topology = TopologyDiagram()

# create nodes, removing last
thetas = np.linspace(0.0, 2*pi, num_sides + 1)[:-1]
radius = diameter / 2.0

for i, theta in enumerate(thetas):

    x = radius * cos(theta)
    y = radius * sin(theta)

    # nodes in the wheel
    topology.add_node(Node(i, [x, y, 0.0]))

# deviation edges in the perimeter of the wheel tension
for u, v in pairwise(list(range(num_sides)) + [0]):
    topology.add_edge(DeviationEdge(u, v, force=tension_force))

# internal deviation edges are in compression
half_num_sides = num_sides / 2.0

for u in range(int(half_num_sides)):
    v = int(u + half_num_sides)
    topology.add_edge(DeviationEdge(u, v, force=compression_force))

# ------------------------------------------------------------------------------
# Generate trails and auto generate auxiliary trails
# ------------------------------------------------------------------------------

topology.auxiliary_trail_length = appendix_length * -1.0
topology.build_trails(auxiliary_trails=True)

# ------------------------------------------------------------------------------
# Compute a state of static equilibrium
# ------------------------------------------------------------------------------

form = static_equilibrium(topology, eta=1e-6, tmax=100)

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

# create optimizer
opt = Optimizer()

# add constraint: force in axiliary trail edges should be zero
for edge in topology.auxiliary_trail_edges():
    opt.add_constraint(TrailEdgeForceConstraint(edge, force=0.0))

# add optimization parameters
# the forces in all the deviation edges are allowed to change
for edge in topology.deviation_edges():
    # compression bounds
    low_bound, up_bound = (bound, bound)
    # tension bounds
    if topology.edge_force(edge) > 0.0:
        low_bound, up_bound = (bound, bound)

    opt.add_parameter(DeviationEdgeParameter(edge, low_bound, up_bound))

# optimize
start = time()
form_opt = opt.solve_nlopt(topology, algorithm="LBFGS", iters=1000, eps=1e-6)

# print out results
print("----------")
print(f"Optimizer. # Parameters {opt.number_of_parameters()}, # Constraints {opt.number_of_constraints()}")
print(f"Optimization elapsed time: {time() - start}")
print(f"Final value of the objective function: {opt.penalty}")
print(f"Norm of the gradient of the objective function: {opt.gradient_norm}")

# ------------------------------------------------------------------------------
# Plot results
# ------------------------------------------------------------------------------

ns = 0.45
shift = diameter * 1.4
plotter = Plotter(figsize=(16.0, 9.0))

# plot topology diagram
plotter.add(topology, nodesize=ns)

# plot translated form diagram
T = Translation.from_vector([shift, 0.0, 0.0])
plotter.add(form.transformed(T), nodesize=ns)

# plot translated optimized form diagram
T = Translation.from_vector([shift * 2.0, 0.0, 0.0])
plotter.add(form_opt.transformed(T), nodesize=ns)

# show scene
plotter.zoom_extents(padding=-0.3)
plotter.show()
