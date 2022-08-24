from compas_cem.optimization.parameters import NodeParameter


__all__ = ["OriginNodeXParameter",
           "OriginNodeYParameter",
           "OriginNodeZParameter"]

# ------------------------------------------------------------------------------
# Origin Node Parameter on X
# ------------------------------------------------------------------------------


class OriginNodeXParameter(NodeParameter):
    """
    Sets the X coordinate of an origin node as an optimization parameter.
    """
    def __init__(self, key=None, bound_low=None, bound_up=None):
        super(OriginNodeXParameter, self).__init__(key, bound_low, bound_up)
        self._attr_name = "x"

# ------------------------------------------------------------------------------
# Origin Node Parameter on Y
# ------------------------------------------------------------------------------


class OriginNodeYParameter(NodeParameter):
    """
    Sets the Y coordinate of an origin node as an optimization parameter.
    """
    def __init__(self, key=None, bound_low=None, bound_up=None):
        super(OriginNodeYParameter, self).__init__(key, bound_low, bound_up)
        self._attr_name = "y"

# ------------------------------------------------------------------------------
# Origin Node Parameter on Z
# ------------------------------------------------------------------------------


class OriginNodeZParameter(NodeParameter):
    """
    Sets the Z coordinate of an origin node as an optimization parameter.
    """
    def __init__(self, key=None, bound_low=None, bound_up=None):
        super(OriginNodeZParameter, self).__init__(key, bound_low, bound_up)
        self._attr_name = "z"

# ------------------------------------------------------------------------------
# Main function
# ------------------------------------------------------------------------------


if __name__ == "__main__":

    from compas.geometry import Point

    from compas_cem.diagrams import TopologyDiagram

    from compas_cem.elements import Node
    from compas_cem.elements import TrailEdge
    from compas_cem.elements import DeviationEdge

    from compas_cem.loads import NodeLoad

    from compas_cem.supports import NodeSupport

    from compas_cem.equilibrium import static_equilibrium

    from compas_cem.optimization import Optimizer
    from compas_cem.optimization import DeviationEdgeParameter
    from compas_cem.optimization import TrailEdgeParameter

    from compas_cem.optimization import PointConstraint

    from compas_cem.plotters import Plotter

    # create a topology diagram
    topology = TopologyDiagram()

    # add nodes
    topology.add_node(Node(0, [0.0, 0.0, 0.0]))
    topology.add_node(Node(1, [1.0, 0.0, 0.0]))
    topology.add_node(Node(2, [2.0, 0.0, 0.0]))
    topology.add_node(Node(3, [3.0, 0.0, 0.0]))

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

    # calculate equilibrium
    topology.build_trails()
    form = static_equilibrium(topology)

    # optimization
    optimizer = Optimizer()

    optimizer.add_parameter(OriginNodeYParameter(1, 1.0, 1.0))
    optimizer.add_parameter(DeviationEdgeParameter((1, 2), 1.0, 1.0))
    optimizer.add_parameter(TrailEdgeParameter((2, 3), 1.0, 1.0))

    point_a = Point(1.0, -0.5, 0.0)
    optimizer.add_constraint((PointConstraint(1, point_a)))

    point_b = Point(3.0, -0.707, 0.0)
    optimizer.add_constraint((PointConstraint(3, point_b)))

    # optimize
    eps = 1e-6
    cform = optimizer.solve(topology, "LBFGS", eps=eps, verbose=True)
    assert optimizer.penalty <= eps

    # plot
    plotter = Plotter()

    plotter.add(form)
    plotter.add(point_b, facecolor=(0, 1, 0))
    plotter.add(point_a, facecolor=(1, 0, 0))
    plotter.add(cform, show_edgetext=True, edgetext="forcelength")

    plotter.zoom_extents()
    plotter.show()
