from compas_cem.optimization.parameters.node import NodeParameter


__all__ = ["NodeLoadXParameter",
           "NodeLoadYParameter",
           "NodeLoadZParameter"]

# ------------------------------------------------------------------------------
# Node Load Parameter - X component
# ------------------------------------------------------------------------------


class NodeLoadXParameter(NodeParameter):
    """
    Sets the X component of a node load as an optimization parameter.
    """
    def __init__(self, key=None, bound_low=None, bound_up=None):
        super(NodeLoadXParameter, self).__init__(key, bound_low, bound_up)
        self._attr_name = "qx"

# ------------------------------------------------------------------------------
# Node Load Parameter - Y component
# ------------------------------------------------------------------------------


class NodeLoadYParameter(NodeParameter):
    """
    Sets the Y component of an node load as an optimization parameter.
    """
    def __init__(self, key=None, bound_low=None, bound_up=None):
        super(NodeLoadYParameter, self).__init__(key, bound_low, bound_up)
        self._attr_name = "qy"

# ------------------------------------------------------------------------------
# Node Load Parameter - Z component
# ------------------------------------------------------------------------------


class NodeLoadZParameter(NodeParameter):
    """
    Sets the Z component of a node load as an optimization parameter.
    """
    def __init__(self, key=None, bound_low=None, bound_up=None):
        super(NodeLoadZParameter, self).__init__(key, bound_low, bound_up)
        self._attr_name = "qz"


if __name__ == "__main__":

    from math import fabs
    from math import pi
    from math import sin
    from math import cos

    from random import choice
    from random import random

    from compas.geometry import add_vectors
    from compas.geometry import Point

    from compas.utilities import pairwise

    from compas_cem.diagrams import TopologyDiagram

    from compas_cem.elements import Node
    from compas_cem.elements import TrailEdge

    from compas_cem.supports import NodeSupport

    from compas_cem.optimization import Optimizer

    from compas_cem.optimization import PointConstraint

    from compas_cem.plotters import Plotter

    # create a topology diagram
    topology = TopologyDiagram()

    # add nodes
    num_nodes = 3
    for i in range(num_nodes):
        topology.add_node(Node(i, [float(i), 0.0, 0.0]))

    # add edges with negative values for a compression-only structure
    length = -1.0
    for i, j in pairwise(range(num_nodes)):
        topology.add_edge(TrailEdge(i, j, length))

    # add supports
    topology.add_support(NodeSupport(int(num_nodes - 1)))

    # calculate trails
    topology.build_trails()

    # optimization
    optimizer = Optimizer()

    # create point constraints at random
    radius = fabs(length)
    pt = [0., 0., 0.]
    points = []
    for i in range(1, num_nodes):
        theta = 0.5 * pi * random()
        x = radius * cos(theta)
        y = radius * sin(theta * choice([-1., 1.]))
        pt = Point(*add_vectors(pt, [x, y, 0.]))
        optimizer.add_constraint(PointConstraint(i, pt))
        points.append(pt)

    for i in range(num_nodes - 1):
        optimizer.add_parameter(NodeLoadXParameter(i, 0.5, 0.5))
        optimizer.add_parameter(NodeLoadYParameter(i, 0.5, 0.5))

    # optimize
    cform = optimizer.solve(topology, "LBFGS", iters=500, verbose=True)

    # plot
    plotter = Plotter(figsize=(16.0, 9.0))

    # plotter.add(form)
    for point in points:
        plotter.add(point, facecolor=(1, 0.5, 0.05))

    plotter.add(cform)

    plotter.zoom_extents()
    plotter.show()
