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
    form : ``FormDiagram``
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
        del form.attributes["trails"]

        return form

# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
