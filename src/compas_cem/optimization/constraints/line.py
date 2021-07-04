from compas.geometry import closest_point_on_line
from compas.geometry import distance_point_point_sqrd

from compas_cem.optimization.constraints import Constraint


__all__ = ["LineConstraint"]


class LineConstraint(Constraint):
    """
    Pulls the xyz position of a node to a target line ray.
    """
    def __init__(self, node=None, line=None, weight=1.0):
        super(LineConstraint, self).__init__(node, line, weight)

    def error(self, data):
        """
        The error between the xyz coords of a node and its closest point on a line.

        Returns
        -------
        error : ``float``
            The squared distance between the two points.
        """
        point_a = self.reference(data)
        point_b = self.target(point_a)

        return distance_point_point_sqrd(point_a, point_b) * self.weight

    def reference(self, data):
        """
        """
        point = data["node_xyz"][self.key()]

        return point

    def target(self, point):
        """
        """
        line = self._target

        return closest_point_on_line(point, line)


if __name__ == "__main__":

    from time import time

    from compas.geometry import Line
    from compas.geometry import Point

    from compas_cem.diagrams import TopologyDiagram

    from compas_cem.elements import Node
    from compas_cem.elements import TrailEdge
    from compas_cem.elements import DeviationEdge

    from compas_cem.loads import NodeLoad

    from compas_cem.supports import NodeSupport

    from compas_cem.optimization import Optimizer
    from compas_cem.optimization import DeviationEdgeParameter
    from compas_cem.optimization import TrailEdgeParameter
    from compas_cem.optimization import PointConstraint

    from compas_cem.equilibrium import static_equilibrium

    from compas_cem.plotters import FormPlotter

    # create a topology diagram
    topology = TopologyDiagram()

    # add nodes
    topology.add_node(Node(0, [0.0, 0.0, 0.0]))
    topology.add_node(Node(1, [1.0, 0.0, 0.0]))
    topology.add_node(Node(2, [2.0, 0.0, 0.0]))
    topology.add_node(Node(3, [3.0, 0.0, 0.0]))
    topology.add_node(Node(4, [4.0, 0.0, 0.0]))

    # add edges with negative values for a compression-only structure
    topology.add_edge(TrailEdge(0, 1, length=-1.0))
    topology.add_edge(DeviationEdge(1, 2, force=-1.0))
    topology.add_edge(TrailEdge(2, 3, length=-1.0))
    topology.add_edge(TrailEdge(3, 4, length=-1.0))

    # add supports
    topology.add_support(NodeSupport(0))
    topology.add_support(NodeSupport(4))

    # add loads
    topology.add_load(NodeLoad(1, [0.0, -1.0, 0.0]))
    topology.add_load(NodeLoad(2, [0.0, -1.0, 0.0]))

    # calculate equilibrium
    topology.build_trails()
    form = static_equilibrium(topology)

    # optimization
    optimizer = Optimizer()

    optimizer.add_parameter(DeviationEdgeParameter((1, 2), 1.0, 1.0))
    optimizer.add_parameter(TrailEdgeParameter((2, 3), 1.0, 1.0))
    optimizer.add_parameter(TrailEdgeParameter((3, 4), 1.0, 1.0))

    point_a = Point(3.0, -0.707, 0.0)
    optimizer.add_constraint((PointConstraint(3, point_a)))

    line = Line([4.0, 0.0, 0.0], [4.0, 1.0, 0.0])
    optimizer.add_constraint((LineConstraint(4, line)))

    # optimization settings
    start = time()
    algo = "LD_LBFGS"  # LN_BOBYQA, LD_LBFGS, LD_MMA
    iters = 100  # 100
    eps = 1e-6  # 1e-4

    # optimize
    form = optimizer.solve_nlopt(topology, algo, iters, eps)

    # print out results
    print("Elapsed time: {}".format(time() - start))
    print("Total error: {}".format(optimizer.penalty))

    # plot
    plotter = FormPlotter(form, figsize=(16, 9))

    plotter.draw_nodes(radius=0.03, text="key-xyz")
    plotter.draw_edges(text="force-length")
    plotter.draw_loads(scale=0.25)
    plotter.draw_reactions(scale=0.10)
    plotter.show()
