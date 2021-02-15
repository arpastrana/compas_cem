from compas_cem.diagrams import FormDiagram
from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.elements import DeviationEdge
from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport
from compas_cem.equilibrium import force_equilibrium
from compas_cem.plotters import FormPlotter


from autograd import grad

def test(x):
    return 2 * x


grad_test = grad(test)       # Obtain its gradient function

for i in range(10):
    print(grad_test(float(i)))

# create a form diagram
form = FormDiagram()

# add nodes
form.add_node(Node(0, [0.0, 0.0, 0.0]))
form.add_node(Node(1, [1.0, 0.0, 0.0]))
form.add_node(Node(2, [2.5, 0.0, 0.0]))
form.add_node(Node(3, [3.5, 0.0, 0.0]))

# add edges with negative values for a compression-only structure
form.add_edge(TrailEdge(0, 1, length=-1.0))
form.add_edge(DeviationEdge(1, 2, force=-1.0))
form.add_edge(TrailEdge(2, 3, length=-1.0))

# add supports
form.add_support(NodeSupport(0))
form.add_support(NodeSupport(3))

# add loads
form.add_load(NodeLoad(1, [0.0, -1.0, 0.0]))
form.add_load(NodeLoad(2, [0.0, -1.0, 0.0]))

# calculate equilibrium
force_equilibrium(form, eps=1e-5, kmax=100, verbose=True)

# plot
plotter = FormPlotter(form, figsize=(16, 9))

plotter.draw_nodes(radius=0.03, text="key-xyz")
plotter.draw_edges(text="force-length")
plotter.draw_loads(scale=-0.25)
plotter.draw_residuals(scale=0.10)
# plotter.show()
