from compas_cem.optimization.constraints import Constraint

from compas.geometry import distance_point_point_sqrd


__all__ = ["TrailEdgeForceConstraint",
           "ReactionForceConstraint"]


class TrailEdgeForceConstraint(Constraint):
    """
    Make a trail edge reach a target force value.
    """
    def __init__(self, edge=None, force=None, weight=1.0):
        # TODO: needs different serialization mechanism?
        super(TrailEdgeForceConstraint, self).__init__(edge, force, weight)

    def error(self, data):
        """
        The error between the current and the target forces in a trail edge.

        Returns
        -------
        error : ``float``
            The squared difference.
        """
        force_a = self.reference(data)
        force_b = self.target()
        diff = force_a - force_b

        return diff * diff * self.weight

    def reference(self, data):
        """
        """
        force = data["trail_forces"][self.key()]

        return force


class ReactionForceConstraint(Constraint):
    """
    Makes the support reaction force at a node match a target vector.
    """
    def __init__(self, node=None, vector=None, weight=1.0):
        super(ReactionForceConstraint, self).__init__(node, vector, weight)

    def error(self, data):
        """
        The error between the current and the target residual force in a node.

        Returns
        -------
        error : ``float``
            The squared difference.
        """
        reaction_a = self.reference(data)
        reaction_b = self.target()

        return distance_point_point_sqrd(reaction_a, reaction_b) * self.weight

    def reference(self, data):
        """
        """
        force = data["reaction_forces"][self.key()]

        return force


if __name__ == "__main__":

    from time import time

    from compas.geometry import Point

    from compas_cem.diagrams import TopologyDiagram

    from compas_cem.elements import Node
    from compas_cem.elements import TrailEdge
    from compas_cem.elements import DeviationEdge

    from compas_cem.loads import NodeLoad

    from compas_cem.supports import NodeSupport

    from compas_cem.optimization import Optimizer
    from compas_cem.optimization import DeviationEdgeParameter

    from compas_cem.optimization import OriginNodeXParameter
    from compas_cem.optimization import OriginNodeYParameter

    from compas_cem.optimization import PointConstraint

    from compas_cem.equilibrium import static_equilibrium

    from compas_cem.plotters import FormPlotter

    # create a topology diagram
    topology = TopologyDiagram()

    # add nodes
    topology.add_node(Node(0, [0.0, 0.0, 0.0]))
    topology.add_node(Node(1, [1.0, 0.0, 0.0]))
    topology.add_node(Node(2, [2.0, 0.0, 0.0]))
    topology.add_node(Node(3, [0.0, 1.0, 0.0]))
    topology.add_node(Node(4, [1.0, 1.0, 0.0]))
    topology.add_node(Node(5, [2.0, 1.0, 0.0]))

    # add edges with negative values for a compression-only structure
    topology.add_edge(TrailEdge(0, 3, length=-1.0))
    topology.add_edge(TrailEdge(1, 4, length=-1.0))
    topology.add_edge(TrailEdge(2, 5, length=-1.0))

    topology.add_edge(DeviationEdge(3, 4, force=-1.0))
    topology.add_edge(DeviationEdge(4, 5, force=-1.0))

    # add supports
    topology.add_support(NodeSupport(0))
    topology.add_support(NodeSupport(1))
    topology.add_support(NodeSupport(2))

    # add loads
    topology.add_load(NodeLoad(4, [0.0, -1.0, 0.0]))

    # calculate equilibrium
    topology.build_trails()
    form = static_equilibrium(topology)

    # optimization
    optimizer = Optimizer()

    # root node parameter in x and y
    for node in (3, 4, 5):
        optimizer.add_parameter(OriginNodeXParameter(node, 1.0, 1.0))
        optimizer.add_parameter(OriginNodeYParameter(node, 1.0, 1.0))

    # deviation edge parameters
    optimizer.add_parameter(DeviationEdgeParameter((3, 4), 1.0, 1.0))
    optimizer.add_parameter(DeviationEdgeParameter((4, 5), 1.0, 1.0))

    # goals
    point_a = Point(0.0, 1.5, 0.0)
    optimizer.add_constraint((PointConstraint(3, point_a)))
    optimizer.add_constraint(TrailEdgeForceConstraint((1, 4), 0.0))
    optimizer.add_constraint(ReactionForceConstraint(1, [0.0, 0.0, 0.0]))

    # optimization settings
    start = time()
    algo = "LD_LBFGS"  # LN_BOBYQA, LD_LBFGS, LD_MMA
    iters = 100  # 100
    eps = 1e-6  # 1e-4

    # optimize
    form = optimizer.solve_nlopt(topology, algo, iters, eps)

    print("Elapsed time: {}".format(time() - start))
    print("Total error: {}".format(optimizer.penalty))

    # plot
    plotter = FormPlotter(form, figsize=(16, 9))

    plotter.draw_nodes(radius=0.03, text="key-xyz")
    plotter.draw_loads(scale=-0.25)
    plotter.draw_reactions(scale=1.0)
    plotter.draw_edges(text="force")
    plotter.show()
