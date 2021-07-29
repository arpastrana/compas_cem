from time import time

from autograd import grad

from compas_cem.diagrams import FormDiagram
from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport
from compas_cem.plotters import FormPlotter

from compas_cem.optimization import Optimizer
from compas_cem.optimization import PointGoal
from compas_cem.optimization import TrailEdgeConstraint

from compas_cem.equilibrium import force_equilibrium
from compas_cem.equilibrium.force_numpy import form_equilibrate_numpy


# global controls
PLOT = False
GRADIENT = True
OPTIMIZE = False

# diagram
form = FormDiagram()

# add nodes
form.add_node(Node(1, xyz=[0, 0, 0]))
form.add_node(Node(2, xyz=[0, 0, 0]))
form.add_node(Node(3, xyz=[0, 0, 0]))

# add edges
form.add_edge(TrailEdge(1, 2, length=-1.0))
form.add_edge(TrailEdge(2, 3, length=-1.0))

# indicate support node
form.add_support(NodeSupport(3))

# add load
form.add_load(NodeLoad(1, vector=[1.0, 0.0, 0.0]))

# calculate equilibrium state
force_equilibrium(form, eps=1e-5, kmax=100, verbose=True)

# create optimizer
optimizer = Optimizer()
# constraint goal
optimizer.add_goal(PointGoal(node=3, point=[3.0, 0.0, 0.0]))
# optimization parameters
optimizer.add_constraint(TrailEdgeConstraint((1, 2), 2.0, 0))
optimizer.add_constraint(TrailEdgeConstraint((2, 3), 2.0, 0))

if GRADIENT:
    # make a copy of the form as it will be modified in-place
    form2 = form.copy()
    # a single gradient run
    # objective function
    def objective_function(x, form_diagram):
        optimizer.form = form_diagram
        optimizer._update_form_edges(x)
        eq_state = form_equilibrate_numpy(form_diagram, kmax=100, eps=1e-5)
        error = optimizer._compute_error(eq_state)
        optimizer.form = None
        return error * 0.5

    # calculate gradient
    X = optimizer.optimization_parameters(form2)
    penalty = objective_function(X, form2)
    grad_func = grad(objective_function)
    grad_value = grad_func(X, form2)

    print(f"X: {X}")
    print(f"penalty: {penalty}")
    print(f"gradient: {grad_value}")

if OPTIMIZE:
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

    print("Final node coordinates")
    for node in form.nodes():
        print(node, ":", form.node_coordinates(node))

    print("Final trail edge attributes")
    for edge in form.trail_edges():
        print(edge, ":", form.edge_attribute(edge, name="length"))

if PLOT:
    plotter = FormPlotter(form, figsize=(16, 9))

    plotter.draw_nodes(radius=0.03, text="key-xyz")
    plotter.draw_edges(text="length")

    plotter.draw_loads(scale=-0.1)
    plotter.draw_residuals(scale=-0.10)
    plotter.show()
