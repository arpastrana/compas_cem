from math import pi as PI

from compas_cem.diagrams import TopologyDiagram

from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.elements import DeviationEdge

from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport

from compas_cem.equilibrium import static_equilibrium as form_finding

from compas_plotters import Plotter
from compas_cem.plotters import TopologyArtist
from compas_cem.plotters import FormArtist
from compas.geometry import Translation
from compas.geometry import Rotation


# create a topology diagram
topology = TopologyDiagram()

# add nodes
topology.add_node(Node(0, [0.0, 0.0, 0.0]))
topology.add_node(Node(1, [1.0, 0.0, 0.0]))
topology.add_node(Node(2, [2.5, 0.0, 0.0]))
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
form = form_finding(topology, eta=1e-6, tmax=100, verbose=True)

# plot
plotter = Plotter(figsize=(16, 10))

R = Rotation.from_axis_and_angle([0.0, 0.0, 1.0], PI/2, [1.75, 0.0, 0.0])
plotter.add(topology.transformed(R),
            artist_type=TopologyArtist,
            nodesize=0.2,
            show_loads=True,
            nodetext='key',
            show_nodetext=True,
            edgetext=False,
            show_edgetext=False)

T = Translation.from_vector([4.0, 0.0, 0.0])
edgewidth = {edge: -2 * form.edge_force(edge) for edge in form.edges()}
plotter.add(form.transformed(T),
            show_nodes=True,
            artist_type=FormArtist,
            nodesize=0.15,
            edgewidth=edgewidth,
            show_loads=True,
            show_reactions=True,
            reactionscale=0.5,
            loadscale=0.5,
            nodetext='keyxyz',
            show_nodetext=True,
            edgetext='forcelength',
            show_edgetext=True)

plotter.zoom_extents()
plotter.show()
