from math import sqrt

from compas.geometry import Translation

from compas_cem.diagrams import TopologyDiagram

from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.elements import DeviationEdge
from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport

from compas_cem.equilibrium import static_equilibrium

from compas_cem.optimization import Optimizer
from compas_cem.optimization import TrailEdgeForceConstraint
from compas_cem.optimization import DeviationEdgeParameter

from compas_cem.plotters import Plotter


# ------------------------------------------------------------------------------
# Instantiate a topology diagram
# ------------------------------------------------------------------------------

topology = TopologyDiagram()

# ------------------------------------------------------------------------------
# Add nodes
# ------------------------------------------------------------------------------

width = 4.0
height = width / 2

topology.add_node(Node(1, [-width / 2.0, height, 0.0]))
topology.add_node(Node(2, [width / 2.0, height, 0.0]))
topology.add_node(Node(3, [0.0, height / 2.5, 0.0]))
topology.add_node(Node(4, [0.0, 0.0, 0.0]))

# ------------------------------------------------------------------------------
# Add edges
# ------------------------------------------------------------------------------

topology.add_edge(TrailEdge(3, 4, length=-height/2))
topology.add_edge(DeviationEdge(1, 3, force=-sqrt(4.0)))
topology.add_edge(DeviationEdge(2, 3, force=-sqrt(2.0)))
topology.add_edge(DeviationEdge(1, 2, force=2.0))

# ------------------------------------------------------------------------------
# Add supports
# ------------------------------------------------------------------------------

topology.add_support(NodeSupport(4))

# ------------------------------------------------------------------------------
# Add loads
# ------------------------------------------------------------------------------

topology.add_load(NodeLoad(1, [0.0, -1.0, 0.0]))
topology.add_load(NodeLoad(2, [0.0, -1.0, 0.0]))

# ------------------------------------------------------------------------------
# Build trails and auto generate auxiliary trails
# ------------------------------------------------------------------------------

topology.build_trails(auxiliary_trails=True)

# ------------------------------------------------------------------------------
# Compute a state of static equilibrium
# ------------------------------------------------------------------------------

form = static_equilibrium(topology, eta=1e-5, tmax=100)

# ------------------------------------------------------------------------------
# Minimize the forces in the axiliary trails
# ------------------------------------------------------------------------------

optimizer = Optimizer()

# add goal constraints
for edge in topology.auxiliary_trail_edges():
    optimizer.add_constraint(TrailEdgeForceConstraint(edge, force=0.0))
    optimizer.add_constraint(TrailEdgeForceConstraint(edge, force=0.0))

# add parameters
optimizer.add_parameter(DeviationEdgeParameter((1, 2), 1.0, 10.0))
optimizer.add_parameter(DeviationEdgeParameter((1, 3), 1.0, 10.0))
optimizer.add_parameter(DeviationEdgeParameter((2, 3), 10.0, 1.0))

# optimize
form_opt = optimizer.solve_nlopt(topology, "SLSQP", 100, 1e-6)

# print out value of the objective function, should be a small number
print("Total value of the objective function: {}".format(optimizer.penalty))
print("Norm of the gradient of the objective function: {}".format(optimizer.gradient_norm))

# ------------------------------------------------------------------------------
# Plot results
# ------------------------------------------------------------------------------

ns = 0.3
shift = width * 1.2
plotter = Plotter(figsize=(16.0, 9.0))

# plot topology diagram
plotter.add(topology,
            nodesize=ns,
            show_nodetext=True,
            nodetext="key")

# plot translated form diagram
T = Translation.from_vector([shift, 0.0, 0.0])
plotter.add(form.transformed(T),
            nodesize=ns,
            show_nodetext=True,
            nodetext="key",
            show_edgetext=True,
            edgetext="force")

# plot translated optimized form diagram
T = Translation.from_vector([shift * 2.0, 0.0, 0.0])
plotter.add(form_opt.transformed(T),
            nodesize=ns,
            show_nodetext=True,
            nodetext="key",
            show_edgetext=True,
            edgetext="force")

# show scene
plotter.zoom_extents(padding=-1.2)
plotter.show()
