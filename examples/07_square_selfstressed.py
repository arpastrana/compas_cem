from time import time

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


# ------------------------------------------------------------------------------
# Form Diagram
# ------------------------------------------------------------------------------

# topology lists

deviation_tension = [(0, 1), (1, 2), (2, 3), (3, 0)]
deviation_compression = [(0, 2), (1, 3)]
trail_tension = [(0, 4), (1, 5), (2, 6), (3, 7)]
node_support = [4, 5, 6, 7]

# create a form diagram
form = FormDiagram()


# add 1 x 1 square module nodes
side_length = 1.0

form.add_node(Node(0, [0.0, 0.0, 0.0]))
form.add_node(Node(1, [side_length, 0.0, 0.0]))
form.add_node(Node(2, [side_length, side_length, 0.0]))
form.add_node(Node(3, [0.0, side_length, 0.0]))

# add appendix modules
appendix_length =side_length / 4.0

form.add_node(Node(4, [0.0, -appendix_length, 0.0]))
form.add_node(Node(5, [side_length, -appendix_length, 0.0]))
form.add_node(Node(6, [side_length, side_length + appendix_length, 0.0]))
form.add_node(Node(7, [0.0, side_length + appendix_length, 0.0]))

# add tension deviation edges
tension_force = +1.0
for u, v in deviation_tension:
    form.add_edge(DeviationEdge(u, v, force=tension_force))

# add compression deviation edges:
compression_force = -1.0
for u, v in deviation_compression:
    form.add_edge(DeviationEdge(u, v, force=compression_force))

# add trail edges
for u, v in trail_tension:
    form.add_edge(TrailEdge(u, v, length=appendix_length))

# add supports
for node in node_support:
    form.add_support(NodeSupport(node))

# ------------------------------------------------------------------------------
# Force equilibrium
# ------------------------------------------------------------------------------

force_equilibrium(form, eps=1e-5, kmax=100)

# ------------------------------------------------------------------------------
# Print out
# ------------------------------------------------------------------------------

print("Final trail edge attributes")
for edge in form.trail_edges():
    force = form.edge_force(edge)
    print(f"Edge: {edge} Force: {force}")

print("Final deviation edge attributes")
for edge in form.deviation_edges():
    force = form.edge_force(edge)
    print(f"Edge: {edge} Force: {force}")

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

# create optimizer
optimizer = Optimizer()

# add goals
# for edge in trail_tension:
    # optimizer.add_goal(TrailEdgeForceGoal(edge, force=0.0))

for node in form.support_nodes():
    optimizer.add_goal(NodeResidualGoal(node, residual_vector=[0.0, 0.0, 0.0]))

# add optimization variables
# tension edges
for edge in deviation_tension:
    optimizer.add_constraint(DeviationEdgeConstraint(edge, 0.0, 5.0))
# compression edges
for edge in deviation_compression:
    optimizer.add_constraint(DeviationEdgeConstraint(edge, 5.0, 0.0))


# optimize
start = time()

# optimization constants
opt_algorithm = "LD_LBFGS"  # LN_BOBYQA / LD_LBFGS / LD_SLSQP
iters = 1000  # 100
stopval = 1e-6  # 1e-4
step_size = 1e-3  # 1e-4

# optimize
# x_opt, l_opt = optimizer.solve_nlopt(form,
#                                      opt_algorithm,
#                                      iters,
#                                      stopval,
#                                      step_size,
#                                      mode="autodiff",
#                                      verbose=False)

# # print out results
# print("Elapsed time: {}".format(time() - start))
# print("Total error: {}".format(l_opt))

# ------------------------------------------------------------------------------
# Print out
# ------------------------------------------------------------------------------

print("Final trail edge attributes")
for edge in form.trail_edges():
    force = form.edge_force(edge)
    print(f"Edge: {edge} Force: {force}")

print("Final deviation edge attributes")
for edge in form.deviation_edges():
    force = form.edge_force(edge)
    print(f"Edge: {edge} Force: {force}")

# ------------------------------------------------------------------------------
# Plot
# ------------------------------------------------------------------------------

plotter = FormPlotter(form, figsize=(16, 9))

plotter.draw_nodes(radius=0.03, text="key-xyz")
plotter.draw_edges(text="force-length")

plotter.draw_loads(scale=0.1)
plotter.draw_residuals(scale=0.10)
plotter.show()
