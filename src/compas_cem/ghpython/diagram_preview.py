"""
Draw styled form and topology diagrams in the Rhino viewport and output them as
model objects.
"""

from typing import NamedTuple

import Grasshopper
import Rhino
import System
from compas_rhino.conversions import point_to_rhino

from compas_cem import ARROW_HEADPORTION
from compas_cem import ARROW_HEADWIDTH
from compas_cem import COLORS

__all__ = ["FormPreview", "TopologyPreview"]

# Millimeters per pixel at 96 dpi, so Print Display shows baked lines at their preview width.
PLOT_WEIGHT_PER_PIXEL = 25.4 / 96.0
NODE_DIAMETER = 8.0
PIPE_SIDES = 8
# Five pixels on, three off: Rhino reads only the low byte of a line pattern.
DASH_PATTERN = 0x1F1F1F1F


class PreviewLine(NamedTuple):
    """
    A Rhino line to draw, with its color, its width in whole pixels, whether
    it is dashed, and for a force its arrowhead and the material that shades it.
    """

    line: object
    color: object
    width: int
    is_dashed: bool
    head_mesh: object
    material: object


class FormPreview:
    """
    The Rhino geometry of a styled form diagram, ready to draw and to output.

    Parameters
    ----------
    drawing :
        The styled form diagram.
    is_thickened :
        Whether the nodes are spheres, the edges pipes and the forces solid
        arrows, all meshes, rather than points and lines.

    Attributes
    ----------
    node_objects :
        One model object per node: a colored point, or a colored sphere mesh
        when thickened.
    support_objects :
        One model object per support node: a colored point, or a colored
        sphere mesh when thickened.
    edge_objects :
        One model object per edge: a line with its color and plot weight, or a
        colored pipe mesh when thickened.
    load_objects :
        One model object per load: a line with its color and plot weight, or a
        colored arrow mesh when thickened.
    reaction_objects :
        One model object per reaction force: a line with its color and plot
        weight, or a colored arrow mesh when thickened.
    clipping_box :
        The box that holds everything the preview draws.

    Notes
    -----
    The geometry is converted once per solution, so a viewport redraw only
    loops over Rhino objects; thickened meshes are merged into one mesh per
    color for drawing. The model objects carry the color and the plot weight
    of what is drawn, so baking them reproduces the preview, except for the
    arrowheads of force lines: Rhino 8 model objects drop curve decorations.
    """

    def __init__(self, drawing, is_thickened=False):
        document = Rhino.RhinoDoc.ActiveDoc
        styled_lines = drawing.edges + drawing.loads + drawing.reactions

        self._lines = []
        self._points = []
        self._meshes = []
        if is_thickened:
            node_meshes = [_sphere_mesh(item) for item in drawing.nodes]
            support_meshes = [_sphere_mesh(item) for item in drawing.support_nodes]
            edge_meshes = [_pipe_mesh(item) for item in drawing.edges]
            load_meshes = [_arrow_mesh(item) for item in drawing.loads]
            reaction_meshes = [_arrow_mesh(item) for item in drawing.reactions]

            self.node_objects = _model_meshes(document, drawing.nodes, node_meshes)
            self.support_objects = _model_meshes(
                document, drawing.support_nodes, support_meshes
            )
            self.edge_objects = _model_meshes(document, drawing.edges, edge_meshes)
            self.load_objects = _model_meshes(document, drawing.loads, load_meshes)
            self.reaction_objects = _model_meshes(
                document, drawing.reactions, reaction_meshes
            )

            styled_items = drawing.nodes + styled_lines
            meshes = node_meshes + edge_meshes + load_meshes + reaction_meshes
            self._meshes = _preview_meshes(styled_items, meshes)
        else:
            self.node_objects = [_model_point(document, item) for item in drawing.nodes]
            self.support_objects = [
                _model_point(document, item) for item in drawing.support_nodes
            ]
            self.edge_objects = [_model_line(document, item) for item in drawing.edges]
            self.load_objects = [_model_line(document, item) for item in drawing.loads]
            self.reaction_objects = [
                _model_line(document, item) for item in drawing.reactions
            ]

            self._lines = [_preview_line(item) for item in styled_lines]
            self._points = [_preview_point(item) for item in drawing.nodes]

        self._labels = [_preview_label(item) for item in drawing.labels]

        self.clipping_box = _bounding_box(
            self._lines, self._meshes, self._points, self._labels
        )

    def draw_wires(self, display, selected_color=None):
        """
        Draw the lines, their arrowheads, the nodes and the labels of the
        preview in a viewport.

        Parameters
        ----------
        display :
            The display pipeline of the viewport.
        selected_color :
            The color that marks a selected component. If `None`, everything
            is drawn in its own color.

        Notes
        -----
        An arrowhead is the cone of a thickened arrow, shaded here rather than
        in the mesh pass so it shows in wireframe views too.
        """
        _draw_wires(display, self._lines, self._points, self._labels, selected_color)

    def draw_meshes(self, display, selected_material=None):
        """
        Draw the thickened meshes of the preview in a viewport, shaded.

        Parameters
        ----------
        display :
            The display pipeline of the viewport.
        selected_material :
            The material that marks a selected component. If `None`, every
            mesh is shaded in its own color.
        """
        for mesh, material in self._meshes:
            shade = material if selected_material is None else selected_material
            display.DrawMeshShaded(mesh, shade)


class TopologyPreview:
    """
    The Rhino geometry of a styled topology diagram, ready to draw and to
    output.

    Parameters
    ----------
    drawing :
        The styled topology diagram.

    Attributes
    ----------
    node_objects :
        One model object per node, as a colored point.
    origin_objects :
        One model object per origin node, as a colored point.
    support_objects :
        One model object per support node, as a colored point.
    edge_objects :
        One model object per edge, as a line with its color and plot weight.
    trail_edge_objects :
        One model object per trail edge, as a line with its color and plot
        weight.
    deviation_edge_objects :
        One model object per deviation edge, as a line with its color and plot
        weight.
    trail_objects :
        One model object per trail, as a polyline with its color and plot
        weight.
    load_objects :
        Two model objects per loaded node, the lines of its cross.
    clipping_box :
        The box that holds everything the preview draws.

    Notes
    -----
    The preview draws the nodes, the edges, the load crosses and the labels;
    the subsets in the other outputs repeat them. Deviation edges are dashed in
    the viewport only, since baking a dashed linetype would add one to the
    document.
    """

    def __init__(self, drawing):
        document = Rhino.RhinoDoc.ActiveDoc

        self.node_objects = [_model_point(document, item) for item in drawing.nodes]
        self.origin_objects = [
            _model_point(document, item) for item in drawing.origin_nodes
        ]
        self.support_objects = [
            _model_point(document, item) for item in drawing.support_nodes
        ]
        self.edge_objects = [_model_line(document, item) for item in drawing.edges]
        self.trail_edge_objects = [
            _model_line(document, item) for item in drawing.trail_edges
        ]
        self.deviation_edge_objects = [
            _model_line(document, item) for item in drawing.deviation_edges
        ]
        self.trail_objects = [
            _model_polyline(document, item) for item in drawing.trails
        ]
        self.load_objects = [_model_line(document, item) for item in drawing.loads]

        self._lines = [_preview_line(item) for item in drawing.edges]
        self._crosses = [_preview_line(item) for item in drawing.loads]
        self._points = [_preview_point(item) for item in drawing.nodes]
        self._labels = [_preview_label(item) for item in drawing.labels]

        box_lines = self._lines + self._crosses
        self.clipping_box = _bounding_box(box_lines, [], self._points, self._labels)

    def draw_wires(self, display, selected_color=None):
        """
        Draw the edges, the nodes, the labels and the load crosses of the
        preview in a viewport.

        Parameters
        ----------
        display :
            The display pipeline of the viewport.
        selected_color :
            The color that marks a selected component. If `None`, everything
            is drawn in its own color.

        Notes
        -----
        The crosses are drawn last, over the nodes they mark, as the topology
        plotter draws them over its node markers.
        """
        _draw_wires(display, self._lines, self._points, self._labels, selected_color)
        for item in self._crosses:
            line_color = item.color if selected_color is None else selected_color
            display.DrawLine(item.line, line_color, item.width)


def _draw_wires(display, lines, points, labels, selected_color):
    """
    Draw preview lines, their arrowheads, nodes and labels in a viewport, all
    in the selection color when one is given.
    """
    stroke_color = System.Drawing.Color.FromArgb(*COLORS["edge"])
    dot_color = System.Drawing.Color.White
    style = Rhino.Display.PointStyle.RoundSimple
    selected_material = None
    if selected_color is not None:
        selected_material = Rhino.Display.DisplayMaterial(selected_color)

    for item in lines:
        line_color = item.color if selected_color is None else selected_color
        if item.is_dashed:
            display.DrawPatternedLine(item.line, line_color, DASH_PATTERN, item.width)
        else:
            display.DrawLine(item.line, line_color, item.width)
        if item.head_mesh is None:
            continue
        shade = item.material if selected_material is None else selected_material
        display.DrawMeshShaded(item.head_mesh, shade)

    for point, color in points:
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

    for point, text in labels:
        display.DrawDot(point, text, dot_color, stroke_color)


def _bounding_box(lines, meshes, points, labels):
    """
    The box that holds every preview line, mesh, node and label.
    """
    box_meshes = [mesh for mesh, _ in meshes]
    box_meshes += [item.head_mesh for item in lines if item.head_mesh]

    corners = System.Collections.Generic.List[Rhino.Geometry.Point3d]()
    for item in lines:
        corners.Add(item.line.From)
        corners.Add(item.line.To)
    for mesh in box_meshes:
        box = mesh.GetBoundingBox(True)
        corners.Add(box.Min)
        corners.Add(box.Max)
    for point, _ in points:
        corners.Add(point)
    for point, _ in labels:
        corners.Add(point)

    if corners.Count == 0:
        return Rhino.Geometry.BoundingBox.Empty

    return Rhino.Geometry.BoundingBox(corners)


def _arrow_head(line):
    """
    The cone of an arrowhead at the end of a line and the point where its base
    meets the shaft.

    Notes
    -----
    The head takes `ARROW_HEADPORTION` of the line's length and its radius is
    `ARROW_HEADWIDTH` of it, as jax_fdm draws an arrow.
    """
    direction = line.Direction
    direction.Unitize()
    head_length = ARROW_HEADPORTION * line.Length
    head_radius = ARROW_HEADWIDTH * line.Length
    base = line.To - direction * head_length

    # A cone's apex sits at its plane's origin, so the head's plane faces back from the tip.
    backward = -direction
    plane = Rhino.Geometry.Plane(line.To, backward)
    cone = Rhino.Geometry.Cone(plane, head_length, head_radius)
    head_mesh = Rhino.Geometry.Mesh.CreateFromCone(cone, 1, PIPE_SIDES, True)

    return head_mesh, base


def _sphere_mesh(item):
    """
    Mesh a styled point as a sphere of its radius.
    """
    center = point_to_rhino(item.point)
    sphere = Rhino.Geometry.Sphere(center, item.radius)

    return Rhino.Geometry.Mesh.CreateFromSphere(sphere, PIPE_SIDES, PIPE_SIDES // 2)


def _pipe_mesh(item):
    """
    Mesh a styled line as a capped pipe of its radius, or `None` if it has no
    length.

    Notes
    -----
    A fresh cylinder per line costs as much as transforming a copy of one unit
    cylinder, since calling into Rhino dominates either way.
    """
    start = point_to_rhino(item.start)
    end = point_to_rhino(item.end)
    line = Rhino.Geometry.Line(start, end)
    if line.Length <= 0.0:
        return None

    plane = Rhino.Geometry.Plane(start, line.Direction)
    circle = Rhino.Geometry.Circle(plane, item.radius)
    cylinder = Rhino.Geometry.Cylinder(circle, line.Length)

    return Rhino.Geometry.Mesh.CreateFromCylinder(cylinder, 1, PIPE_SIDES, True, True)


def _arrow_mesh(item):
    """
    Mesh a styled line as a solid arrow: a cylinder body and a cone head, or
    `None` if it has no length.

    Notes
    -----
    The body's radius is the styled radius and the head has the proportions
    of every arrowhead. The whole arrow first moves along its own direction
    by its offset, so it clears the sphere of the node it touches.
    """
    line_start = point_to_rhino(item.start)
    line_end = point_to_rhino(item.end)
    line = Rhino.Geometry.Line(line_start, line_end)
    if line.Length <= 0.0:
        return None

    direction = line.Direction
    direction.Unitize()
    shift = direction * item.offset
    start = line_start + shift
    end = line_end + shift
    arrow_line = Rhino.Geometry.Line(start, end)
    head_mesh, base = _arrow_head(arrow_line)

    body_plane = Rhino.Geometry.Plane(start, direction)
    body_circle = Rhino.Geometry.Circle(body_plane, item.radius)
    body_length = start.DistanceTo(base)
    body_cylinder = Rhino.Geometry.Cylinder(body_circle, body_length)
    arrow = Rhino.Geometry.Mesh.CreateFromCylinder(
        body_cylinder, 1, PIPE_SIDES, True, True
    )
    arrow.Append(head_mesh)

    return arrow


def _preview_meshes(items, meshes):
    """
    Merge the meshes of styled items into one mesh per color, each with a
    material of that color.
    """
    groups = {}
    for item, mesh in zip(items, meshes):
        if mesh is not None:
            groups.setdefault(item.color, []).append(mesh)

    merged_meshes = []
    for rgb, group in groups.items():
        merged = Rhino.Geometry.Mesh()
        merged.Append(group)
        material = Rhino.Display.DisplayMaterial(_system_color(rgb))
        merged_meshes.append((merged, material))

    return merged_meshes


def _system_color(rgb):
    """
    Convert an RGB triple into a .NET color.
    """
    return System.Drawing.Color.FromArgb(*rgb)


def _preview_line(item):
    """
    Convert a styled line into a line to preview; a force line stops at the
    base of its arrowhead.
    """
    start = point_to_rhino(item.start)
    end = point_to_rhino(item.end)
    line = Rhino.Geometry.Line(start, end)
    color = _system_color(item.color)
    width = max(1, int(round(item.width)))

    head_mesh = None
    material = None
    if item.is_arrow and line.Length > 0.0:
        head_mesh, base = _arrow_head(line)
        line = Rhino.Geometry.Line(start, base)
        material = Rhino.Display.DisplayMaterial(color)

    return PreviewLine(
        line=line,
        color=color,
        width=width,
        is_dashed=item.is_dashed,
        head_mesh=head_mesh,
        material=material,
    )


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


def _model_polyline(document, item):
    """
    Wrap a styled polyline as a model object that bakes with its color and its
    plot weight.
    """
    attributes = _object_attributes(item.color)
    attributes.PlotWeightSource = (
        Rhino.DocObjects.ObjectPlotWeightSource.PlotWeightFromObject
    )
    attributes.PlotWeight = item.width * PLOT_WEIGHT_PER_PIXEL

    points = [point_to_rhino(point) for point in item.points]
    curve = Rhino.Geometry.PolylineCurve(points)

    return Grasshopper.Rhinoceros.Model.ModelObject(document, attributes, curve)


def _model_meshes(document, items, meshes):
    """
    Wrap the meshes of styled items as model objects that bake with their
    colors, keeping `None` where a line had no length so the list stays aligned
    with its keys.
    """
    objects = []
    for item, mesh in zip(items, meshes):
        if mesh is None:
            objects.append(None)
            continue
        attributes = _object_attributes(item.color)
        model_object = Grasshopper.Rhinoceros.Model.ModelObject(
            document, attributes, mesh
        )
        objects.append(model_object)

    return objects
