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
from compas_cem.ghpython.diagram_display import StyledLine

__all__ = ["FormPreview", "TopologyPreview"]

# Millimeters per pixel at 96 dpi, so Print Display shows baked lines at their preview width.
PLOT_WEIGHT_PER_PIXEL = 25.4 / 96.0
NODE_DIAMETER = 8.0
# Rhino's arrowhead on a force line, in pixels: four per pixel of line width, at least twelve.
HEAD_PIXELS_PER_WIDTH = 4.0
HEAD_PIXELS_MIN = 12.0
# Five pixels on, three off: Rhino reads only the low byte of a line pattern.
DASH_PATTERN = 0x1F1F1F1F


class PreviewLine(NamedTuple):
    """
    A Rhino line to draw, with its color, its width in whole pixels, whether
    it is dashed, and whether it draws a force with an arrowhead.
    """

    line: object
    color: object
    width: int
    is_dashed: bool
    is_arrow: bool


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
    thick_sides :
        The number of faces around every thickened pipe, arrow and sphere.

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

    def __init__(self, drawing, is_thickened=False, thick_sides=8):
        document = Rhino.RhinoDoc.ActiveDoc
        styled_lines = drawing.edges + drawing.loads + drawing.reactions
        self._drawing = drawing
        self._is_thickened = is_thickened
        self._thick_sides = thick_sides

        self._lines = []
        self._points = []
        self._meshes = []
        if is_thickened:
            sides = thick_sides
            node_meshes = [_sphere_mesh(item, sides) for item in drawing.nodes]
            support_meshes = [
                _sphere_mesh(item, sides) for item in drawing.support_nodes
            ]
            edge_meshes = [_pipe_mesh(item, sides) for item in drawing.edges]
            load_meshes = [_arrow_mesh(item, sides) for item in drawing.loads]
            reaction_meshes = [_arrow_mesh(item, sides) for item in drawing.reactions]

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
        A force line ends in Rhino's own arrowhead, sized on screen, as
        Grasshopper draws a vector.
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

    def bake(self, document):
        """
        Add what the preview draws to a Rhino document, one sublayer per
        category under `COMPAS CEM::Form`.

        Parameters
        ----------
        document :
            The Rhino document to bake into.

        Returns
        -------
        ids :
            The ids of the baked objects.

        Notes
        -----
        Lines bake with their colors and plot weights, and force lines with an
        arrowhead; thickened meshes bake with their colors. The support nodes,
        which repeat nodes, and the labels are not baked.
        """
        drawing = self._drawing
        groups = [
            ("Nodes", drawing.nodes),
            ("Edges", drawing.edges),
            ("Loads", drawing.loads),
            ("Reactions", drawing.reactions),
        ]
        if self._is_thickened:
            records = _mesh_records(groups, self._thick_sides)
        else:
            records = _line_records(groups)
        ids = _bake_records(document, "COMPAS CEM::Form", records)

        return ids


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
        self._drawing = drawing

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

    def bake(self, document):
        """
        Add what the preview draws to a Rhino document, one sublayer per
        category under `COMPAS CEM::Topology`.

        Parameters
        ----------
        document :
            The Rhino document to bake into.

        Returns
        -------
        ids :
            The ids of the baked objects.

        Notes
        -----
        Lines bake with their colors and plot weights, and deviation edges with
        Rhino's dashed linetype. The origin and support nodes, which repeat
        nodes, the trails, which repeat trail edges, and the labels are not
        baked.
        """
        drawing = self._drawing
        groups = [
            ("Nodes", drawing.nodes),
            ("Trail Edges", drawing.trail_edges),
            ("Deviation Edges", drawing.deviation_edges),
            ("Loads", drawing.loads),
        ]
        records = _line_records(groups)
        ids = _bake_records(document, "COMPAS CEM::Topology", records)

        return ids


class BakeRecord(NamedTuple):
    """
    A Rhino object to bake: its sublayer, its geometry and attributes, and
    whether it takes the dashed linetype.
    """

    sublayer: str
    geometry: object
    attributes: object
    is_dashed: bool


def _line_records(groups):
    """
    The bake records of styled points and lines, grouped by sublayer: points
    with their colors, lines with their colors and plot weights, force lines
    with an arrowhead.
    """
    records = []
    for sublayer, items in groups:
        for item in items:
            if isinstance(item, StyledLine):
                geometry = _line_curve(item)
                attributes = _weighted_attributes(item.color, item.width)
                if item.is_arrow:
                    decoration = Rhino.DocObjects.ObjectDecoration.EndArrowhead
                    attributes.ObjectDecoration = decoration
                is_dashed = item.is_dashed
            else:
                geometry = _point_geometry(item)
                attributes = _object_attributes(item.color)
                is_dashed = False
            record = BakeRecord(sublayer, geometry, attributes, is_dashed)
            records.append(record)

    return records


def _mesh_records(groups, sides):
    """
    The bake records of thickened nodes, edges and forces, grouped by sublayer,
    as meshes with their colors.
    """
    records = []
    for sublayer, items in groups:
        for item in items:
            if not isinstance(item, StyledLine):
                mesh = _sphere_mesh(item, sides)
            elif item.is_arrow:
                mesh = _arrow_mesh(item, sides)
            else:
                mesh = _pipe_mesh(item, sides)
            if mesh is None:
                continue
            attributes = _object_attributes(item.color)
            record = BakeRecord(sublayer, mesh, attributes, False)
            records.append(record)

    return records


def _bake_records(document, root, records):
    """
    Add bake records to a Rhino document as one undo step, each on its
    sublayer of the root layer, and return their ids.
    """
    undo_record = document.BeginUndoRecord("Bake COMPAS CEM")
    layer_indices = {}
    materials = {}
    dashed_index = None

    ids = []
    for record in records:
        if record.sublayer not in layer_indices:
            path = "{}::{}".format(root, record.sublayer)
            layer_indices[record.sublayer] = _layer_index(document, path)
        attributes = record.attributes
        attributes.LayerIndex = layer_indices[record.sublayer]
        if record.is_dashed:
            if dashed_index is None:
                dashed_index = _dashed_linetype(document)
            attributes.LinetypeSource = (
                Rhino.DocObjects.ObjectLinetypeSource.LinetypeFromObject
            )
            attributes.LinetypeIndex = dashed_index
        if isinstance(record.geometry, Rhino.Geometry.Mesh):
            color = attributes.ObjectColor
            if color.ToArgb() not in materials:
                materials[color.ToArgb()] = _color_material(document, color)
            attributes.RenderMaterial = materials[color.ToArgb()]
        object_id = document.Objects.Add(record.geometry, attributes)
        ids.append(object_id)

    document.EndUndoRecord(undo_record)
    document.Views.Redraw()

    return ids


def _color_material(document, color):
    """
    The render material of a color in a document, named after the color's hex
    code and created if the document has none by that name.

    Notes
    -----
    Rendered views shade a mesh with its render material, not its display
    color, so a baked mesh needs one to keep its color there.
    """
    name = "COMPAS CEM #{:02X}{:02X}{:02X}".format(color.R, color.G, color.B)
    for content in document.RenderMaterials:
        if content.Name == name:
            return content

    material = Rhino.DocObjects.Material()
    material.Name = name
    material.DiffuseColor = color
    render_material = Rhino.Render.RenderMaterial.CreateBasicMaterial(
        material, document
    )
    render_material.Name = name
    document.RenderMaterials.Add(render_material)

    return render_material


def _layer_index(document, path):
    """
    The index of a nested layer, given by its full path, created level by level
    if it is missing.
    """
    names = path.split("::")
    parent_id = System.Guid.Empty
    index = -1
    for depth in range(len(names)):
        partial_path = "::".join(names[: depth + 1])
        index = document.Layers.FindByFullPath(partial_path, -1)
        if index < 0:
            layer = Rhino.DocObjects.Layer()
            layer.Name = names[depth]
            layer.ParentLayerId = parent_id
            index = document.Layers.Add(layer)
        parent_id = document.Layers[index].Id

    return index


def _dashed_linetype(document):
    """
    The index of Rhino's dashed linetype in a document, after loading Rhino's
    standard linetypes if the document has none by that name.
    """
    index = document.Linetypes.Find("Dashed")
    if index < 0:
        document.Linetypes.LoadDefaultLinetypes()
        index = document.Linetypes.Find("Dashed")

    return index


def _draw_wires(display, lines, points, labels, selected_color):
    """
    Draw preview lines, their arrowheads, nodes and labels in a viewport, all
    in the selection color when one is given.
    """
    stroke_color = System.Drawing.Color.FromArgb(*COLORS["edge"])
    dot_color = System.Drawing.Color.White
    style = Rhino.Display.PointStyle.RoundSimple

    for item in lines:
        line_color = item.color if selected_color is None else selected_color
        if item.is_dashed:
            display.DrawPatternedLine(item.line, line_color, DASH_PATTERN, item.width)
        else:
            display.DrawLine(item.line, line_color, item.width)
        if item.is_arrow:
            head_pixels = max(HEAD_PIXELS_MIN, HEAD_PIXELS_PER_WIDTH * item.width)
            display.DrawArrow(item.line, line_color, head_pixels, 0.0)

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

    clipping_box = Rhino.Geometry.BoundingBox(corners)

    return clipping_box


def _arrow_head(line, sides):
    """
    The cone of an arrowhead at the end of a line and the point where its base
    meets the shaft.

    Notes
    -----
    The head takes `ARROW_HEADPORTION` of the line's length and its radius is
    `ARROW_HEADWIDTH` of it.
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
    head_mesh = Rhino.Geometry.Mesh.CreateFromCone(cone, 1, sides, True)

    return head_mesh, base


def _sphere_mesh(item, sides):
    """
    Mesh a styled point as a sphere of its radius.
    """
    center = point_to_rhino(item.point)
    sphere = Rhino.Geometry.Sphere(center, item.radius)
    sphere_mesh = Rhino.Geometry.Mesh.CreateFromSphere(sphere, sides, sides // 2)

    return sphere_mesh


def _pipe_mesh(item, sides):
    """
    Mesh a styled line as a capped pipe of its radius, shortened at both ends
    by its trim, or `None` if nothing of it is left.

    Notes
    -----
    The trim ends a pipe where its rim meets the node sphere. A fresh cylinder
    per line costs as much as transforming a copy of one unit cylinder, since
    calling into Rhino dominates either way.
    """
    start = point_to_rhino(item.start)
    end = point_to_rhino(item.end)
    line = Rhino.Geometry.Line(start, end)
    pipe_length = line.Length - 2.0 * item.trim
    if pipe_length <= 0.0:
        return None

    direction = line.Direction
    direction.Unitize()
    pipe_start = start + direction * item.trim
    plane = Rhino.Geometry.Plane(pipe_start, direction)
    circle = Rhino.Geometry.Circle(plane, item.radius)
    cylinder = Rhino.Geometry.Cylinder(circle, pipe_length)
    pipe_mesh = Rhino.Geometry.Mesh.CreateFromCylinder(cylinder, 1, sides, True, True)

    return pipe_mesh


def _arrow_mesh(item, sides):
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
    head_mesh, base = _arrow_head(arrow_line, sides)

    body_plane = Rhino.Geometry.Plane(start, direction)
    body_circle = Rhino.Geometry.Circle(body_plane, item.radius)
    body_length = start.DistanceTo(base)
    body_cylinder = Rhino.Geometry.Cylinder(body_circle, body_length)
    arrow = Rhino.Geometry.Mesh.CreateFromCylinder(body_cylinder, 1, sides, True, True)
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
    color = System.Drawing.Color.FromArgb(*rgb)

    return color


def _preview_line(item):
    """
    Convert a styled line into a line to preview.
    """
    start = point_to_rhino(item.start)
    end = point_to_rhino(item.end)
    line = Rhino.Geometry.Line(start, end)
    color = _system_color(item.color)
    width = max(1, int(round(item.width)))
    is_arrow = item.is_arrow and line.Length > 0.0

    preview_line = PreviewLine(
        line=line,
        color=color,
        width=width,
        is_dashed=item.is_dashed,
        is_arrow=is_arrow,
    )

    return preview_line


def _preview_point(item):
    """
    Convert a styled point into a Rhino point and its color.
    """
    location = point_to_rhino(item.point)
    color = _system_color(item.color)

    return location, color


def _preview_label(item):
    """
    Convert a text label into a Rhino point and its text.
    """
    location = point_to_rhino(item.point)

    return location, item.text


def _object_attributes(rgb):
    """
    Rhino object attributes that take their color from the object.
    """
    attributes = Rhino.DocObjects.ObjectAttributes()
    attributes.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
    attributes.ObjectColor = _system_color(rgb)

    return attributes


def _point_geometry(item):
    """
    Convert a styled point into a Rhino point object.
    """
    location = point_to_rhino(item.point)
    point = Rhino.Geometry.Point(location)

    return point


def _line_curve(item):
    """
    Convert a styled line into a Rhino line curve.
    """
    start = point_to_rhino(item.start)
    end = point_to_rhino(item.end)
    curve = Rhino.Geometry.LineCurve(start, end)

    return curve


def _model_point(document, item):
    """
    Wrap a styled point as a model object that carries its color.
    """
    attributes = _object_attributes(item.color)
    point = _point_geometry(item)
    model_object = Grasshopper.Rhinoceros.Model.ModelObject(document, attributes, point)

    return model_object


def _model_line(document, item):
    """
    Wrap a styled line as a model object that carries its color and its plot
    weight.
    """
    attributes = _weighted_attributes(item.color, item.width)
    curve = _line_curve(item)
    model_object = Grasshopper.Rhinoceros.Model.ModelObject(document, attributes, curve)

    return model_object


def _model_polyline(document, item):
    """
    Wrap a styled polyline as a model object that bakes with its color and its
    plot weight.
    """
    attributes = _weighted_attributes(item.color, item.width)
    points = [point_to_rhino(point) for point in item.points]
    curve = Rhino.Geometry.PolylineCurve(points)
    model_object = Grasshopper.Rhinoceros.Model.ModelObject(document, attributes, curve)

    return model_object


def _weighted_attributes(rgb, width):
    """
    Rhino object attributes that take their color and their plot weight, the
    pixel width at 96 dpi, from the object.
    """
    attributes = _object_attributes(rgb)
    attributes.PlotWeightSource = (
        Rhino.DocObjects.ObjectPlotWeightSource.PlotWeightFromObject
    )
    attributes.PlotWeight = width * PLOT_WEIGHT_PER_PIXEL

    return attributes


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
