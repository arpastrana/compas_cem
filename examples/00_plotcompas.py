#!/usr/bin/env python3

from compas.datastructures import Network
from compas_plotters import Plotter


# create network
network = Network()
network.add_node(0, x=0.0, y=0.0)
network.add_node(1, x=1.0, y=0.0)
network.add_node(2, x=1.0, y=-1.0)
network.add_node(3, x=0.0, y=-1.0)
network.add_edge(0, 1)
network.add_edge(1, 2)
network.add_edge(2, 3)
network.add_edge(3, 0)

# plot
plotter = Plotter()
plotter.add(network, nodesize=0.1)
breakpoint()
plotter.zoom_extents()
plotter.show()
