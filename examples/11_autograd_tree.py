from time import time
from math import sqrt

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
from compas_cem.optimization import TrailEdgeForceGoal
from compas_cem.optimization import DeviationEdgeConstraint

from compas_cem.equilibrium.force_numpy import form_equilibrate_numpy

from autograd import grad


# global controls
PLOT = False
OPTIMIZE = False

# create a form diagram
form = FormDiagram()

width = 4
height = width / 2

# add nodes
form.add_node(Node(1, [-width / 2, height, 0.0]))
form.add_node(Node(2, [width / 2, height, 0.0]))
form.add_node(Node(3, [0.0, height / 2, 0.0]))
form.add_node(Node(4, [0.0, 0.0, 0.0]))
form.add_node(Node(5, [width / 2, height / 2, 0.0]))

# add edges with negative values for a compression-only structure
form.add_edge(TrailEdge(1, 3, length=-sqrt((width / 2) * (width / 2) + (height / 2) * (height / 2))))
form.add_edge(TrailEdge(3, 4, length=-height / 2))
form.add_edge(TrailEdge(2, 5, length=-height/2))

form.add_edge(DeviationEdge(1, 2, force=2.0))  # 2
form.add_edge(DeviationEdge(2, 3, force=-sqrt(4.0)))  # -sqrt(5)

# add supports
form.add_support(NodeSupport(4))
form.add_support(NodeSupport(5))

# add loads
form.add_load(NodeLoad(1, [0.0, -1.0, 0.0]))
form.add_load(NodeLoad(2, [0.0, -1.0, 0.0]))

# autograd stuff
# create optimizer
optimizer = Optimizer()

# add goal
# optimizer.add_goal(PointGoal(node=4, point=[0.0, 0.0, 0.0]))
optimizer.add_goal(TrailEdgeForceGoal(edge=(2, 5), force=0.0))

# add parameters
optimizer.add_constraint(DeviationEdgeConstraint((1, 2), 1.0, 10.0))
optimizer.add_constraint(DeviationEdgeConstraint((2, 3), 10.0, 1.0))

# incoming egde vectors
print(form.incoming_edge_vectors(2, form.connected_deviation_edges(2), normalize=True))

# static equilibrium
form.trails()
force_equilibrium(form, eps=1e-5, kmax=100, verbose=True)

# autograd stuff
def loss(x, form):
    optimizer.form = form
    optimizer._update_form_edges(x)
    eq_state = form_equilibrate_numpy(form, kmax=100, eps=1e-5)
    error = optimizer._compute_error(eq_state)
    optimizer.form = None
    return error


X = optimizer.optimization_parameters(form)
print(f"X: {X}")
error = optimizer._grad_optimize_form(X, form)
print(f"error: {error}")
my_func = loss
grad_func = grad(loss)
grad_val = grad_func(X, form)
print(f"grad: {grad_val}")


if OPTIMIZE:
    force_equilibrium(form, eps=1e-5, kmax=100, verbose=True)

    # optimize
    start = time()

    # optimization constants
    opt_algorithm = "LD_SLSQP"
    iters = 100  # 100
    stopval = 1e-4  # 1e-4
    step_size = 1e-6  # 1e-4

    # optimize
    x_opt, l_opt = optimizer.solve_nlopt(form,
                                         opt_algorithm,
                                         iters, stopval,
                                         step_size,
                                         mode="autodiff",
                                         verbose=False)

    # print out results
    print("Elapsed time: {}".format(time() - start))
    print("Total error: {}".format(l_opt))

    # calculate equilibrium
    print("Final node coordinates")
    for node in form.nodes():
        print(node, ":", form.node_coordinates(node))

    print("Final trail edge attributes")
    for edge in form.trail_edges():
        print(edge, ":", form.edge_attribute(edge, name="length"))

    print("Final deviation edge attributes")
    for edge in form.deviation_edges():
        print(edge, ":", form.edge_attribute(edge, name="force"))


# plot
if PLOT:

    plotter = FormPlotter(form, figsize=(16, 9))

    plotter.draw_nodes(radius=0.03, text="key-xyz")
    plotter.draw_edges(text="force-length")

    plotter.draw_loads(scale=-0.1)
    plotter.draw_residuals(scale=-0.10)
    plotter.show()
