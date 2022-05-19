
from math import pi as PI

from compas_cem.diagrams import TopologyDiagram

from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.elements import DeviationEdge

from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport

from compas_cem.equilibrium import static_equilibrium as form_finding

from compas.geometry import Translation
from compas.geometry import Rotation
from compas.geometry import Sphere
from compas_view2.app import App


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

# calculate static equilibrium
form = form_finding(topology, eta=1e-6, tmax=100, verbose=True)

viewer = App()
# viewer.add(Sphere([0, 0, 0], 1.0))
viewer.add(form)
# viewer.add(Sphere([0, 0, 0], 1.0),
#           u=64,
#           v=64,
#           show_points=True,
#           show_lines=True,
#           show_faces=True,
#           color=(0.7, 0., 0.7),
#           pointcolor=(1.0, 0.0, 0.0),
#           linecolor=(0.0, 0.0, 1.0),
#           facecolor=(0.0, 1.0, 1.0),
#           pointsize=10,
#           linewidth=2,
#           opacity=0.5,
#           is_selected=False,
#           is_visible=True)
viewer.show()
