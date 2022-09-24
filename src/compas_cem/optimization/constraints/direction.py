from compas.geometry import normalize_vector
from compas.geometry import subtract_vectors
from compas.geometry import length_vector_sqrd
from compas.geometry import scale_vector

from compas_cem.optimization.constraints import VectorConstraint


__all__ = ["EdgeDirectionConstraint"]


class EdgeDirectionConstraint(VectorConstraint):
    """
    Align the direction of a trail or a deviation edge with a target vector.
    """
    def __init__(self, edge=None, vector=None, weight=1.0):
        super(EdgeDirectionConstraint, self).__init__(edge, vector, weight)

    def target(self, reference):
        """
        The target vector.
        """
        return normalize_vector(self._target)

    def reference(self, data):
        """
        The edge direction.
        """
        # cosine_similarity = dot_vectors(u, v) / (length_vector(u) * length_vector(v))
        # 1 - fabs(cosine_similarity)
        u, v = self.key()
        vector = subtract_vectors(data["node_xyz"][v], data["node_xyz"][u])
        return scale_vector(vector, 1.0 / (length_vector_sqrd(vector) ** 0.5))


if __name__ == "__main__":

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

    topology.add_edge(TrailEdge(0, 1, length=-1.0))
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

    vector = [-2.0, -1.0, 0.0]
    constraint = EdgeDirectionConstraint((0, 1), vector)
    opt.add_constraint(constraint)

    # ------------------------------------------------------------------------------
    # Define optimization parameters
    # ------------------------------------------------------------------------------

    for edge in topology.deviation_edges():
        opt.add_parameter(DeviationEdgeParameter(edge, bound_low=10.0, bound_up=10.0))

    # ------------------------------------------------------------------------------
    # Optimization
    # ------------------------------------------------------------------------------

    # optimize
    form_opt = opt.solve(topology=topology,
                         algorithm="SLSQP",
                         verbose=True)

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
