from compas.geometry import closest_point_on_segment
from compas.geometry._core.distance import closest_points_in_cloud_numpy

from compas.utilities import pairwise

from compas_cem.optimization.constraints import VectorConstraint


__all__ = ["PolylineConstraint"]


class PolylineConstraint(VectorConstraint):
    """
    Pulls the xyz position of a node to a target polyline.
    """
    def __init__(self, node=None, polyline=None, weight=1.0):
        super(PolylineConstraint, self).__init__(node, polyline, weight)

    def reference(self, data):
        """
        The current xyz coordinates of the node.
        """
        return data["node_xyz"][self.key()]

    def target(self, reference):
        """
        The closest point on the target polyline.
        """
        polyline = self._target
        return self._closest_point_on_polyline(reference, polyline)

    @staticmethod
    def _closest_point_on_polyline(point, polyline):
        """
        The closest point on a polyline.

        Notes
        -----
        This is a reimplementation of a compas method.
        The compas method did not support autograd transforms.
        """
        cloud = []

        for segment in pairwise(polyline):
            cloud.append(closest_point_on_segment(point, segment))

        indices = closest_points_in_cloud_numpy([point], cloud, distances=False)

        return cloud[indices[0]]


if __name__ == "__main__":

    from math import fabs
    from math import pi
    from math import sin
    from math import cos

    from random import choice
    from random import random
    from random import seed

    from compas.geometry import add_vectors
    from compas.geometry import Point
    from compas.geometry import Polyline

    from compas_cem.diagrams import TopologyDiagram

    from compas_cem.elements import Node
    from compas_cem.elements import TrailEdge

    from compas_cem.loads import NodeLoad

    from compas_cem.supports import NodeSupport

    from compas_cem.optimization import Optimizer

    from compas_cem.optimization import PointConstraint
    from compas_cem.optimization import NodeLoadXParameter
    from compas_cem.optimization import NodeLoadYParameter

    from compas_cem.plotters import Plotter

    # set random seed
    seed(0)

    # create a topology diagram
    topology = TopologyDiagram()

    # add nodes
    num_nodes = 7
    for i in range(num_nodes):
        topology.add_node(Node(i, [float(i), 0.0, 0.0]))

    # add edges with negative values for a compression-only structure
    length = -1.0
    for i, j in pairwise(range(num_nodes)):
        topology.add_edge(TrailEdge(i, j, length))

    # add supports
    topology.add_support(NodeSupport(int(num_nodes - 1)))

    # add initial load
    for i in range(1, num_nodes - 1):
        topology.add_load(NodeLoad(i, [-0.1, 0.0, 0.0]))

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
        points.append(pt)

    polyline = Polyline(points)
    for i in range(1, num_nodes - 1):
        optimizer.add_constraint(PolylineConstraint(i, polyline))

    optimizer.add_constraint(PointConstraint(num_nodes - 1, points[-1]))

    for i in range(num_nodes - 1):
        optimizer.add_parameter(NodeLoadXParameter(i, 0.5, 0.5))
        optimizer.add_parameter(NodeLoadYParameter(i, 0.5, 0.5))

    # optimize
    cform = optimizer.solve(topology, "SLSQP", iters=500, verbose=True)

    # plot
    plotter = Plotter(figsize=(16.0, 9.0))

    plotter.add(polyline, linewidth=0.5, show_points=False)

    for point in points:
        plotter.add(point, facecolor=(1, 0.5, 0.05))

    plotter.add(topology)
    plotter.add(cform)

    plotter.zoom_extents()
    plotter.show()
