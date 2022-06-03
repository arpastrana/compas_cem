from math import copysign
from math import fabs

from compas.geometry import add_vectors
from compas.geometry import length_vector
from compas.geometry import scale_vector
from compas.geometry import normalize_vector
from compas.geometry import translate_points

from compas.geometry import Vector
from compas.geometry import Point

from compas.utilities import geometric_key

from compas_view2.objects import BufferObject

from compas_cem import COLORS

from compas_cem.viewers import DiagramObject

from compas.colors import Color

__all__ = ["FormDiagramObject"]


class FormDiagramObject(DiagramObject):
    """
    An object to display a form diagram.

    Parameter
    ----------
    form_diagram : :class:`~compas_cem.diagrams.FormDiagram`
        The form diagram to plot.
    """
    def __init__(self, form_diagram, **kwargs):
        super(FormDiagramObject, self).__init__(form_diagram, **kwargs)


if __name__ == "__main__":
    pass
