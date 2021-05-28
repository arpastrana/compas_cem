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



form = FormDiagram()

# add nodes
form.add_node(Node(0, xyz=[0.0, 0.0, 0.0]))
form.add_node(Node(1, xyz=[1.0, 0.0, 0.0]))

# add edge
form.add_edge(TrailEdge(0, 1, length=2.0))

# add support
form.add_support(NodeSupport(1))

# add loads
form.add_load(NodeLoad(0, [1.0, 1.0, 0.0]))

# calculate equilibrium
force_equilibrium(form, eps=1e-5, kmax=100)

optimizer = Optimizer()
optimizer.add_goal(PointGoal(node=1, point=[-2.0, -2.0, 0.0]))
optimizer.add_constraint(TrailEdgeConstraint((0, 1), 0.0, 4.0))

# optimize
# optimization constants
opt_algorithm = "LD_SLSQP"
iters = 100  # 100
stopval = 1e-4  # 1e-4
step_size = 1e-6  # 1e-4
optimizer.solve_nlopt(form, opt_algorithm, iters, stopval, step_size, mode="autodiff", verbose=False)

# plot
plotter = FormPlotter(form, figsize=(16, 9))

plotter.draw_nodes(radius=0.03, text="key-xyz")
plotter.draw_edges(text="force-length")

plotter.draw_loads(scale=-0.5)
plotter.draw_residuals(scale=-0.5)
plotter.show()





            

        
