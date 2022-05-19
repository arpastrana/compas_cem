from compas_cem.diagrams import TopologyDiagram

from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.elements import DeviationEdge

from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport

from compas_cem.equilibrium import static_equilibrium

from compas_plotters import Plotter
from compas_cem.plotters import TopologyArtist
from compas_cem.plotters import FormArtist
from compas.geometry import Translation


# ------------------------------------------------------------------------------
# Instantiate a topology diagram
# ------------------------------------------------------------------------------

topology = TopologyDiagram()

# ------------------------------------------------------------------------------
# Add nodes
# ------------------------------------------------------------------------------

topology.add_node(Node(0, [0.0, 0.0, 0.0]))
topology.add_node(Node(1, [1.0, 0.0, 0.0]))
topology.add_node(Node(2, [2.5, 0.0, 0.0]))
topology.add_node(Node(3, [3.5, 0.0, 0.0]))

# ------------------------------------------------------------------------------
# Add edges
# ------------------------------------------------------------------------------

topology.add_edge(TrailEdge(0, 1, length=-1.0))
topology.add_edge(DeviationEdge(1, 2, force=-1.0))
topology.add_edge(TrailEdge(2, 3, length=-1.0))

# ------------------------------------------------------------------------------
# Add supports
# ------------------------------------------------------------------------------

topology.add_support(NodeSupport(0))
topology.add_support(NodeSupport(3))

# ------------------------------------------------------------------------------
# Add loads
# ------------------------------------------------------------------------------

topology.add_load(NodeLoad(1, [0.0, -1.0, 0.0]))
topology.add_load(NodeLoad(2, [0.0, -1.0, 0.0]))

# ------------------------------------------------------------------------------
# Build trails automatically
# ------------------------------------------------------------------------------

topology.build_trails()

# ------------------------------------------------------------------------------
# Compute a state of static equilibrium
# ------------------------------------------------------------------------------

form = static_equilibrium(topology, eta=1e-6, tmax=100, verbose=True)

# ------------------------------------------------------------------------------
# Plot results
# ------------------------------------------------------------------------------

# instantiate a plotter
plotter = Plotter()

# add topology diagram to scene
plotter.add(topology, artist_type=TopologyArtist, nodesize=0.2)

# add shifted form diagram to the scene
form = form.transformed(Translation.from_vector([0.0, -1.0, 0.0]))
plotter.add(form, artist_type=FormArtist, nodesize=0.2)

# show plotter contents
plotter.zoom_extents()
plotter.show()
