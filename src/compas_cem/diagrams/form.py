from compas_cem.diagrams import Diagram


__all__ = ["FormDiagram"]

# ==============================================================================
# Form Diagram
# ==============================================================================


class FormDiagram(Diagram):
    """
    The heart of life.

    Parameters
    ----------
    *args : ``list``
        Arguments.
    **kwargs : ``dict``
        Keyword arguments.

    Returns
    -------
    form : :class:`compas_cem.diagrams.FormDiagram`
        A form diagram.
    """
    def __init__(self, *args, **kwargs):
        super(FormDiagram, self).__init__(*args, **kwargs)

# ==============================================================================
# Constructors
# ==============================================================================

    @classmethod
    def from_topology_diagram(cls, topology):
        """
        Construct the base of a form diagram from a topology diagram.
        """
        form = topology.copy(cls=cls)

        del form.attributes["_trails"]
        del form.attributes["_auxiliary_trails"]
        del form.attributes["_aux_length"]
        del form.attributes["_aux_vector"]

        return form

# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
