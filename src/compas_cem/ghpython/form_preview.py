"""
Draw a styled form diagram in the Rhino viewport and output it as model objects.
"""

import Grasshopper
import Rhino
import System
from compas_rhino.conversions import point_to_rhino

from compas_cem import COLORS

__all__ = ["FormPreview"]

# Millimeters per pixel at 96 dpi, so Print Display shows baked lines at their preview width.
PLOT_WEIGHT_PER_PIXEL = 25.4 / 96.0
NODE_DIAMETER = 8.0


class FormPreview:
    """
    The Rhino geometry of a styled form diagram, ready to draw and to output.

    Parameters
    ----------
    drawing :
        The styled form diagram.

    Attributes
    ----------
    node_objects :
        One model object per node, as a colored point.
    support_objects :
        One model object per support node, as a colored point.
    edge_objects :
        One model object per edge, as a line with its color and plot weight.
    load_objects :
        One model object per load, as a line with its color and plot weight.
    reaction_objects :
        One model object per reaction force, as a line with its color and plot
        weight.
    clipping_box :
        The box that holds everything the preview draws.

    Notes
    -----
    The geometry is converted once per solution, so a viewport redraw only
    loops over Rhino objects. The model objects carry the color and the plot
    weight of what is drawn, so baking them reproduces the preview, except for
    the arrowheads of the forces: Rhino 8 model objects drop curve decorations.
    """

    def __init__(self, drawing):
        document = Rhino.RhinoDoc.ActiveDoc

        self.node_objects = [_model_point(document, item) for item in drawing.nodes]
        self.support_objects = [
            _model_point(document, item) for item in drawing.support_nodes
        ]
        self.edge_objects = [_model_line(document, item) for item in drawing.edges]
        self.load_objects = [_model_line(document, item) for item in drawing.loads]
        self.reaction_objects = [
            _model_line(document, item) for item in drawing.reactions
        ]

        styled_lines = drawing.edges + drawing.loads + drawing.reactions
        self._lines = [_preview_line(item) for item in styled_lines]
        self._points = [_preview_point(item) for item in drawing.nodes]
        self._labels = [_preview_label(item) for item in drawing.labels]

        self.clipping_box = self._bounding_box()

    def draw_wires(self, display, viewport, selected_color=None):
        """
        Draw the preview in a viewport.

        Parameters
        ----------
        display :
            The display pipeline of the viewport.
        viewport :
            The viewport, which sets the model size of an arrowhead.
        selected_color :
            The color that marks a selected component. If `None`, everything
            is drawn in its own color.

        Notes
        -----
        An arrowhead is a filled triangle with a fixed size on screen, converted
        to model units at its tip on every redraw, because Rhino's own arrowhead
        draws nothing at small sizes in a Grasshopper preview.
        """
        stroke_color = System.Drawing.Color.FromArgb(*COLORS["edge"])
        dot_color = System.Drawing.Color.White
        style = Rhino.Display.PointStyle.RoundSimple

        for line, color, width, is_arrow in self._lines:
            line_color = color if selected_color is None else selected_color
            display.DrawLine(line, line_color, width)
            if not is_arrow:
                continue
            corners = _arrowhead_corners(viewport, line, width)
            if corners:
                display.DrawPolygon(corners, line_color, True)

        for point, color in self._points:
            fill_color = color if selected_color is None else selected_color
            # The size is a diameter in pixels; without that flag it is a radius in model units.
            display.DrawPoint(
                point,
                style,
                stroke_color,
                fill_color,
                NODE_DIAMETER,
                1.0,
                0.0,
                0.0,
                True,
                True,
            )

        for point, text in self._labels:
            display.DrawDot(point, text, dot_color, stroke_color)

    def _bounding_box(self):
        """
        The box that holds every line, node and label of the preview.
        """
        points = System.Collections.Generic.List[Rhino.Geometry.Point3d]()
        for line, _, _, _ in self._lines:
            points.Add(line.From)
            points.Add(line.To)
        for point, _ in self._points:
            points.Add(point)
        for point, _ in self._labels:
            points.Add(point)

        if points.Count == 0:
            return Rhino.Geometry.BoundingBox.Empty

        return Rhino.Geometry.BoundingBox(points)


def _arrowhead_corners(viewport, line, width):
    """
    The corners of a line's arrowhead, sized in pixels from the line width.

    Returns
    -------
    corners :
        The tip and the two base corners, or an empty list if the viewport has
        no scale at the tip or the line points straight at the camera.
    """
    tip = line.To
    is_scaled, pixels_per_unit = viewport.GetWorldToScreenScale(tip)
    if not is_scaled or pixels_per_unit <= 0.0:
        return []

    direction = line.Direction
    side = Rhino.Geometry.Vector3d.CrossProduct(direction, viewport.CameraDirection)
    if not (direction.Unitize() and side.Unitize()):
        return []

    length = (3.0 * width + 8.0) / pixels_per_unit
    half_width = (width + 3.0) / pixels_per_unit
    base = tip - direction * length
    corners = [tip, base + side * half_width, base - side * half_width]

    return corners


def _system_color(rgb):
    """
    Convert an RGB triple into a .NET color.
    """
    return System.Drawing.Color.FromArgb(*rgb)


def _preview_line(item):
    """
    Convert a styled line into a Rhino line, its color, its width in whole
    pixels and whether it ends in an arrowhead.
    """
    start = point_to_rhino(item.start)
    end = point_to_rhino(item.end)
    line = Rhino.Geometry.Line(start, end)
    width = max(1, int(round(item.width)))

    return line, _system_color(item.color), width, item.is_arrow


def _preview_point(item):
    """
    Convert a styled point into a Rhino point and its color.
    """
    return point_to_rhino(item.point), _system_color(item.color)


def _preview_label(item):
    """
    Convert a text label into a Rhino point and its text.
    """
    return point_to_rhino(item.point), item.text


def _object_attributes(rgb):
    """
    Rhino object attributes that take their color from the object.
    """
    attributes = Rhino.DocObjects.ObjectAttributes()
    attributes.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
    attributes.ObjectColor = _system_color(rgb)

    return attributes


def _model_point(document, item):
    """
    Wrap a styled point as a model object that bakes with its color.
    """
    attributes = _object_attributes(item.color)
    location = point_to_rhino(item.point)
    point = Rhino.Geometry.Point(location)

    return Grasshopper.Rhinoceros.Model.ModelObject(document, attributes, point)


def _model_line(document, item):
    """
    Wrap a styled line as a model object that bakes with its color and its
    plot weight.
    """
    attributes = _object_attributes(item.color)
    attributes.PlotWeightSource = (
        Rhino.DocObjects.ObjectPlotWeightSource.PlotWeightFromObject
    )
    attributes.PlotWeight = item.width * PLOT_WEIGHT_PER_PIXEL

    start = point_to_rhino(item.start)
    end = point_to_rhino(item.end)
    curve = Rhino.Geometry.LineCurve(start, end)

    return Grasshopper.Rhinoceros.Model.ModelObject(document, attributes, curve)
