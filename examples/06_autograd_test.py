from compas_cem.diagrams import FormDiagram
from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.elements import DeviationEdge
from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport
from compas_cem.equilibrium import force_equilibrium
from compas_cem.plotters import FormPlotter
from compas_cem.optimization import Optimizer
from compas_cem.optimization import PointGoal
from compas_cem.optimization import TrailEdgeConstraint

# create a form diagram
form = FormDiagram()

# add nodes
form.add_node(Node(0, [0.0, 0.0, 0.0]))
form.add_node(Node(1, [0.0, 0.0, 0.0]))
form.add_node(Node(2, [0.0, 0.0, 0.0]))

# add edges with negative values for a compression-only structure
form.add_edge(TrailEdge(0, 1, length=-1.0))
form.add_edge(TrailEdge(1, 2, length=-0.5))

# add supports
form.add_support(NodeSupport(2))

# add loads
form.add_load(NodeLoad(0, [2.0, 0.0, 0.0]))

# create optimizer
optimizer = Optimizer()

optimizer.add_goal(PointGoal(node=2, point=[3.0, 0.0, 0.0]))
optimizer.add_constraint(TrailEdgeConstraint((1, 2), -2.0, 2.0))

# force_equilibrium(form, eps=1e-5, kmax=100, verbose=True)

# optimize
# start = time()

# optimization constants
opt_algorithm = "LD_SLSQP"  # LN_BOBYQA / LD_LBFGS
# opt_algorithm = "LN_BOBYQA"
iters = 100  # 100
stopval = 1e-4  # 1e-4
step_size = 1e-6  # 1e-4

# optimize
x_opt, l_opt = optimizer.solve_nlopt(form,
                                     opt_algorithm,
                                     iters, stopval,
                                     step_size,
                                     verbose=True)

# print out results
# print("Elapsed time: {}".format(time() - start))
print("Total error: {}".format(l_opt))
# calculate equilibrium

print("Final node coordinates")
for node in form.nodes():
    print(node, ":", form.node_coordinates(node))

print("Final trail edge attributes")
for edge in form.trail_edges():
    print(edge, ":", form.edge_attribute(edge, name="length"))

# plot
plotter = FormPlotter(form, figsize=(16, 9))

plotter.draw_nodes(radius=0.03, text="key-xyz")
plotter.draw_edges(text="length")

plotter.draw_loads(scale=-0.1)
plotter.draw_residuals(scale=-0.10)
plotter.show()
