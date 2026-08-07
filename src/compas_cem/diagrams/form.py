from compas_cem.diagrams import Diagram
from compas_cem.elements import Edge
from compas_cem.elements import Node

__all__ = ["FormDiagram"]

# ==============================================================================
# Form Diagram
# ==============================================================================


class FormDiagram(Diagram):
    """
    The output of the form-finding algorithm.

    A form diagram carries the same nodes and edges as the topology diagram it
    came from, positioned in static equilibrium, with the resulting edge forces
    and support reactions stored on it.

    Parameters
    ----------
    *args :
        Arguments forwarded to the base diagram.
    **kwargs :
        Keyword arguments forwarded to the base diagram.
    """

    def __init__(self, *args, **kwargs):
        super(FormDiagram, self).__init__(*args, **kwargs)

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_topology_diagram(cls, topology):
        """
        Construct a form diagram from a topology diagram.

        Parameters
        ----------
        topology :
            The topology diagram to copy.

        Returns
        -------
        form :
            A form diagram with the same nodes and edges as the topology.

        Notes
        -----
        The trail bookkeeping is dropped, because a form diagram is the result
        of walking the trails rather than a description of them.
        """
        form = topology.copy(cls=cls)

        del form.attributes["_trails"]
        del form.attributes["_auxiliary_trails"]
        del form.attributes["_aux_length"]
        del form.attributes["_aux_vector"]

        return form

    @classmethod
    def from_equilibrium_state(cls, eq_state, structure):
        """
        Build a form diagram from an equilibrium state.

        Parameters
        ----------
        eq_state :
            An equilibrium state computed by the numerical kernel.
        structure :
            The structure the equilibrium state was computed on.

        Returns
        -------
        form :
            A form diagram carrying the equilibrium state.
        """
        return form_from_eqstate(eq_state, structure, cls)


# ==============================================================================
# Helpers
# ==============================================================================


def form_from_eqstate(eqstate, structure, cls=None):
    """
    Generate a form diagram from an equilibrium state calculated with JAX CEM.

    Parameters
    ----------
    eqstate :
        An equilibrium state computed by the numerical kernel.
    structure :
        The structure the equilibrium state was computed on.
    cls :
        The form diagram class to instantiate. Defaults to `FormDiagram`.

    Returns
    -------
    form :
        A form diagram carrying the equilibrium state.
    """
    if cls is None:
        cls = FormDiagram
    form = cls()

    # Add nodes
    for node in structure.nodes:
        form.add_node(Node(int(node)))

    # Assign support nodes
    for node in structure.support_nodes:
        form.node_attribute(int(node), "type", "support")

    # Add edges
    for u, v in structure.edges:
        form.add_edge(Edge(int(u), int(v), {}))

    # Update form attributes
    form_update(form, eqstate, structure)

    return form


def form_update(form, eqstate, structure):
    """
    Update in-place the attributes of a form diagram with an equilibrium state.

    Parameters
    ----------
    form :
        The form diagram to update.
    eqstate :
        An equilibrium state computed by the numerical kernel.
    structure :
        The structure the equilibrium state was computed on.
    """
    xyz = eqstate.xyz.tolist()
    loads = eqstate.loads.tolist()
    reactions = eqstate.reactions.tolist()
    lengths = eqstate.lengths.tolist()
    forces = eqstate.forces.tolist()

    # Update q values and lengths on edges
    for edge in structure.edges:
        idx = structure.edge_index[tuple(edge)]
        form.edge_attribute(edge, name="force", value=forces[idx].pop())
        form.edge_attribute(edge, name="lengths", value=lengths[idx].pop())

    # Update residuals on nodes
    for node in structure.nodes:
        form.node_attributes(node, "xyz", xyz[node])
        form.node_attributes(node, ["rx", "ry", "rz"], reactions[node])
        form.node_attributes(node, ["qx", "qy", "qz"], loads[node])


# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
