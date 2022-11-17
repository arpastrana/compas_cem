from compas.geometry import dot_vectors
from compas.geometry import normalize_vector
from compas.geometry import subtract_vectors
from compas.geometry import length_vector_sqrd
from compas.geometry import scale_vector

from compas_cem.optimization.constraints import VectorConstraint


__all__ = ["EdgeDirectionConstraint"]


class EdgeDirectionConstraint(VectorConstraint):
    """
    Align the direction of a trail or a deviation edge with a target vector.

    Note that the ordering of the nodes of the edge to constrain matters.
    The reference direction of the edge is a vector pointing from its starting node (u),
    towards its end node (v).
    """
    def __init__(self, edge=None, vector=None, weight=1.0):
        super(EdgeDirectionConstraint, self).__init__(edge, vector, weight)

    def target(self, reference):
        """
        The target, unit-length vector.
        """
        target = normalize_vector(self._target)
        return self._aligned_vector(target, reference)

    def reference(self, data):
        """
        The unitized edge direction.
        """
        vector = self._vector_two_points(self.key(), data)
        return self._unitized_vector(vector)

    @staticmethod
    def _vector_two_points(edge, data):
        """
        Create a vector from the XYZ coordinates of two nodes.
        """
        u, v = edge
        return subtract_vectors(data["node_xyz"][v], data["node_xyz"][u])

    @staticmethod
    def _unitized_vector(vector):
        """
        Scale a copy of a vector such that its length is equal to one.
        """
        return scale_vector(vector, 1.0 / (length_vector_sqrd(vector) ** 0.5))

    @staticmethod
    def _aligned_vector(vector, vector_ref):
        """
        Align a vector to another such that their dot product is non-negative.
        """
        if dot_vectors(vector, vector_ref) < 0.0:
            return scale_vector(vector, -1.0)
        return vector


if __name__ == "__main__":

    from math import fabs

    from compas.geometry import Translation

    from compas_cem.diagrams import TopologyDiagram

    from compas_cem.elements import Node
    from compas_cem.elements import TrailEdge
    from compas_cem.elements import DeviationEdge

    from compas_cem.loads import NodeLoad
    from compas_cem.supports import NodeSupport

    from compas_cem.equilibrium import static_equilibrium

    from compas_cem.optimization import Optimizer
    from compas_cem.optimization import DeviationEdgeParameter

    from compas_cem.plotters import Plotter

    # ------------------------------------------------------------------------------
    # Instantiate a topology diagram
    # ------------------------------------------------------------------------------

    topology = TopologyDiagram()

    # ------------------------------------------------------------------------------
    # Add nodes
    # ------------------------------------------------------------------------------

    topology.add_node(Node(0, [0.0, 0.0, 0.0]))
    topology.add_node(Node(1, [1.0, 0.0, 0.0]))
    topology.add_node(Node(2, [2.5, 0.0, 0.0]))
    topology.add_node(Node(3, [3.5, 0.0, 0.0]))

    # ------------------------------------------------------------------------------
    # Add edges
    # ------------------------------------------------------------------------------

    topology.add_edge(TrailEdge(1, 0, length=-1.0))
    topology.add_edge(DeviationEdge(1, 2, force=-1.0))
    topology.add_edge(TrailEdge(2, 3, length=-1.0))

    # ------------------------------------------------------------------------------
    # Add supports
    # ------------------------------------------------------------------------------

    topology.add_support(NodeSupport(0))
    topology.add_support(NodeSupport(3))

    # ------------------------------------------------------------------------------
    # Add loads
    # ------------------------------------------------------------------------------

    topology.add_load(NodeLoad(1, [0.0, -1.0, 0.0]))
    topology.add_load(NodeLoad(2, [0.0, -1.0, 0.0]))

    # ------------------------------------------------------------------------------
    # Build trails automatically
    # ------------------------------------------------------------------------------

    topology.build_trails()

    # ------------------------------------------------------------------------------
    # Compute a state of static equilibrium
    # ------------------------------------------------------------------------------

    form = static_equilibrium(topology, eta=1e-6, tmax=100, verbose=True)

    # ------------------------------------------------------------------------------
    # Initialize optimizer
    # ------------------------------------------------------------------------------

    opt = Optimizer()

    # ------------------------------------------------------------------------------
    # Define constraints
    # ------------------------------------------------------------------------------

    vector = [0.0, -2.0, 0.0]
    for edge in topology.trail_edges():
        constraint = EdgeDirectionConstraint(edge, vector)
        opt.add_constraint(constraint)

    # ------------------------------------------------------------------------------
    # Define optimization parameters
    # ------------------------------------------------------------------------------

    for edge in topology.deviation_edges():
        opt.add_parameter(DeviationEdgeParameter(edge, bound_low=10.0, bound_up=10.0))

    # ------------------------------------------------------------------------------
    # Optimization
    # ------------------------------------------------------------------------------

    form_opt = opt.solve(topology=topology,
                         algorithm="SLSQP",
                         verbose=True)

    # ------------------------------------------------------------------------------
    # Test
    # ------------------------------------------------------------------------------

    for edge in topology.deviation_edges():
        force = fabs(topology.edge_force(edge))
        assert force <= 1e-3, f"Absolute edge force: {force}"

    # ------------------------------------------------------------------------------
    # Plot results
    # ------------------------------------------------------------------------------

    plotter = Plotter()

    # add topology diagram to scene
    plotter.add(topology, show_nodetext=True, nodesize=0.2)

    # add shifted form diagram to the scene
    form = form.transformed(Translation.from_vector([0.0, -1.0, 0.0]))
    plotter.add(form, nodesize=0.2, show_edgetext=True, edgetext="force")

    # add shifted form diagram to the scene
    form_opt = form_opt.transformed(Translation.from_vector([0.0, -2.5, 0.0]))
    plotter.add(form_opt, nodesize=0.2, show_edgetext=True, edgetext="force")

    # show plotter contents
    plotter.zoom_extents()
    plotter.show()
