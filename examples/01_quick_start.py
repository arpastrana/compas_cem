from compas_cem.diagrams import TopologyDiagram

from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.elements import DeviationEdge

from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport

from compas_cem.equilibrium import static_equilibrium

from compas_plotters import Plotter


# create a topology diagram
topology = TopologyDiagram()

# add nodes
topology.add_node(Node(0, [0.0, 0.0, 0.0]))
topology.add_node(Node(1, [1.0, 0.1, 0.0]))
topology.add_node(Node(2, [2.5, 0.1, 0.0]))
topology.add_node(Node(3, [3.5, 0.0, 0.0]))

# add edges with negative values for a compression-only structure
topology.add_edge(TrailEdge(0, 1, length=-1.0))
topology.add_edge(DeviationEdge(1, 2, force=-1.0))
topology.add_edge(TrailEdge(2, 3, length=-1.0))

# add supports
topology.add_support(NodeSupport(0))
topology.add_support(NodeSupport(3))

# add loads
topology.add_load(NodeLoad(1, [0.0, -1.0, 0.0]))
topology.add_load(NodeLoad(2, [0.0, -1.0, 0.0]))

# assemble trails
topology.build_trails()

# calculate equilibrium
form = static_equilibrium(topology, eta=1e-6, tmax=100, verbose=True)

# plot topology
plotter = Plotter()
plotter.add(topology, nodesize=0.2)
plotter.zoom_extents()
plotter.show()

# plot topology
plotter = Plotter()
plotter.add(form, nodesize=0.2)
plotter.zoom_extents()
plotter.show()

# plot topology
# artist.draw_nodes()
# plotter.draw_loads(radius=0.03, draw_arrows=True, scale=0.25)
# plotter.draw_nodes(radius=0.03)
# plotter.draw_edges()
# vb = plotter.viewbox
# print(vb)
# print("artists", plotter.artists)
# plotter.show()

# # plot form
# plotter = FormPlotter(form, figsize=(16, 9))
# plotter.draw_nodes(radius=0.03, text="key-xyz")
# plotter.draw_edges(text="force-length")
# plotter.draw_loads(scale=0.25)
# plotter.draw_reactions(scale=0.25)
# plotter.show()
