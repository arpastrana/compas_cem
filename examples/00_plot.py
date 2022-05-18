from compas_cem.diagrams import TopologyDiagram

from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.elements import DeviationEdge

from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport

from compas_cem.equilibrium import static_equilibrium as form_finding


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

####
from compas_plotters import Plotter
from compas_cem.plotters import TopologyArtist
from compas_cem.plotters import FormArtist
from compas.geometry import Translation
from compas.geometry import Rotation
from math import pi as PI

plotter = Plotter(figsize=(16, 10))

R = Rotation.from_axis_and_angle([0.0, 0.0, 1.0], PI/2, [1.75, 0.0, 0.0])
plotter.add(topology,
            artist_type=TopologyArtist,
            nodesize=0.2,
            show_loads=False,
            nodetext='key',
            show_nodetext=False,
            edgetext='index',
            show_edgetext=False)

T = Translation.from_vector([4.0, 0.0, 0.0])
plotter.add(form.transformed(T),
            artist_type=FormArtist,
            nodesize=0.15,
            edgewidth=2.0,
            show_loads=False,
            show_reactions=False,
            reactionscale=0.5,
            loadscale=0.5,
            nodetext='key-xyz',
            show_nodetext=True,
            edgetext='force',
            show_edgetext=False)


padding = 0.0
matfactor = 0.1
width, height = plotter.figsize
fig_aspect = width / height
data = []
for artist in plotter.artists:
    data += artist.data
x, y = zip(* data)
xmin = min(x)
xmax = max(x)
ymin = min(y)
ymax = max(y)
xspan = xmax - xmin + padding
yspan = ymax - ymin + padding
data_aspect = xspan / yspan
print(xspan, yspan, data_aspect)
# breakpoint()
xlim = [xmin - matfactor * xspan, xmax + matfactor * xspan]
ylim = [ymin - matfactor * yspan, ymax + matfactor * yspan]

# xlim = [xmin, xmax]
# ylim = [ymin, ymax]
# data_aspect_2 = (xlim[1] - xlim[0]) / (ylim[1] - ylim[0])

if data_aspect < fig_aspect:
    print("adjusting xlim")
    scale = fig_aspect / data_aspect
    print("scale", scale)
    # xpad = xspan * (scale - 1) / 2.0 - matfactor * xspan + padding / 2.0
    xpad = 0.5 * (xspan * (scale - 1) + padding) - matfactor * xspan # + 0.5 * padding

    # xpad = xspan * (0.5 * (scale + padding - 1.0) - matfactor)
    xlim[0] -= xpad
    xlim[1] += xpad
    xspan2 = xlim[1] - xlim[0]
    data_aspect_3 = xspan2 / yspan
    print(fig_aspect, data_aspect_3)

else:
    print("adjusting ylim")
    scale = data_aspect / fig_aspect
    # ypad = (yspan * scale - yspan) / 2.0 - matfactor * yspan + padding / 2.0
    ypad = 0.5 * yspan * (scale - 1) - matfactor * yspan + 0.5 * padding
    ylim[0] -= ypad
    ylim[1] += ypad

    # print(data_aspect, data_aspect_2, fig_aspect, scale, xspan / (yspan*scale), yspan, yspan*scale)
    yspan2 = ylim[1] - ylim[0]
    data_aspect_3 = xspan / yspan2
    print(fig_aspect, data_aspect_3)
    # print(ylim)
    # print(yspan, ymin, ymax)
    # ymin -= ypad
    # ymax += ypad
    # print(data_aspect, fig_aspect, xspan/(ymax-ymin+padding))
# assert fig_aspect - data_aspect_3, f"Unequal! ({fig_aspect}, {data_aspect_3})"

plotter.viewbox = (xlim, ylim)
plotter.axes.set_xlim(*xlim)
plotter.axes.set_ylim(*ylim)
plotter.axes.autoscale_view()
# plotter.zoom_extents()  # refine zoomed in view, seems buggy
plotter.show()


# plot topology
# artist.draw_nodes()
# plotter.draw_loads(radius=0.03, draw_arrows=True, scale=0.25)
# plotter.draw_nodes(radius=0.03)
# plotter.draw_edges()
# plotter.show()
