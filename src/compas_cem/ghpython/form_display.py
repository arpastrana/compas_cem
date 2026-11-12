"""
The style rules for drawing a form diagram in Grasshopper, kept free of Rhino.
"""

from dataclasses import dataclass
from math import fabs
from typing import NamedTuple

from compas.geometry import add_vectors
from compas.geometry import length_vector
from compas.geometry import midpoint_point_point
from compas.geometry import scale_vector
from compas.geometry import subtract_vectors

from compas_cem import ARROW_BODYWIDTH
from compas_cem import COLORS

__all__ = [
    "FormDisplaySettings",
    "FormDrawing",
    "StyledLine",
    "StyledPoint",
    "TextLabel",
    "edge_radii",
    "edge_widths",
    "form_drawing",
    "reaction_shifts",
]


@dataclass(frozen=True)
class FormDisplaySettings:
    """
    The settings to draw a form diagram with in Grasshopper.

    Parameters
    ----------
    force_min :
        The smallest load or reaction force magnitude worth drawing.
    force_scale :
        The factor to scale the loads and the reaction forces by.
    width_min :
        The width in pixels of the edge with the smallest absolute force.
    width_max :
        The width in pixels of the edge with the largest absolute force.
    radius_min :
        The pipe radius in model units of the edge with the smallest absolute
        force, when the edges are thickened into pipes.
    radius_max :
        The pipe radius in model units of the edge with the largest absolute
        force, when the edges are thickened into pipes. It is also the radius
        of the thickened nodes, so a node covers every pipe meeting it.
    show_labels :
        Whether to label every drawn edge with its force.

    Notes
    -----
    The settings are a dataclass rather than a named tuple, because Grasshopper
    unpacks a tuple output into its items.
    """

    force_min: float = 1e-3
    force_scale: float = 1.0
    width_min: float = 1.0
    width_max: float = 8.0
    radius_min: float = 0.01
    radius_max: float = 0.1
    show_labels: bool = False

    def __post_init__(self):
        bounds = {
            "width": (self.width_min, self.width_max),
            "radius": (self.radius_min, self.radius_max),
        }
        for name, (low, high) in bounds.items():
            if not 0.0 < low <= high:
                message = "The edge {0}s need 0 < {0}_min <= {0}_max, got {1} and {2}."
                raise ValueError(message.format(name, low, high))


class StyledPoint(NamedTuple):
    """
    A point to draw, with its color and its sphere radius in model units when
    thickened.
    """

    point: list[float]
    color: tuple[int, int, int]
    radius: float


class StyledLine(NamedTuple):
    """
    A line to draw, with its color, its width in pixels, its pipe radius in
    model units, whether it ends in an arrowhead, and how far a thickened
    arrow moves along its own direction to clear the sphere of its node.
    """

    start: list[float]
    end: list[float]
    color: tuple[int, int, int]
    width: float
    radius: float
    is_arrow: bool
    offset: float = 0.0


class TextLabel(NamedTuple):
    """
    A text to draw at a point.
    """

    point: list[float]
    text: str


class FormDrawing(NamedTuple):
    """
    A form diagram styled for drawing.
    """

    nodes: list[StyledPoint]
    support_nodes: list[StyledPoint]
    edges: list[StyledLine]
    loads: list[StyledLine]
    reactions: list[StyledLine]
    labels: list[TextLabel]


def form_drawing(form, node_keys, edge_keys, settings):
    """
    Style a selection of a form diagram for drawing.

    Parameters
    ----------
    form :
        The form diagram to draw.
    node_keys :
        The nodes to draw, with their loads and reaction forces. If `None`,
        every node is drawn.
    edge_keys :
        The edges to draw. If `None`, every edge is drawn.
    settings :
        The display settings.

    Returns
    -------
    drawing :
        The styled nodes, support nodes, edges, loads, reaction forces, and the
        edge labels when the settings show them.

    Notes
    -----
    Every node is colored by whether it is a support, so the support nodes are
    drawn twice, once among the nodes and once on their own. A load arrow
    always ends at its node, so its head touches the node it loads; a reaction
    ends at its support only when it pushes into it.
    """
    nodes = list(form.nodes()) if node_keys is None else list(node_keys)
    edges = list(form.edges()) if edge_keys is None else list(edge_keys)
    supports = [node for node in nodes if form.is_node_support(node)]

    sphere_radius = settings.radius_max
    node_points = [_styled_node(form, node, sphere_radius) for node in nodes]
    support_points = [_styled_node(form, node, sphere_radius) for node in supports]

    widths = edge_widths(form, settings.width_min, settings.width_max)
    radii = edge_radii(form, settings.radius_min, settings.radius_max)
    edge_lines = []
    for edge in edges:
        key = tuple(edge)
        line = _styled_edge(form, edge, widths[key], radii[key])
        edge_lines.append(line)

    load_shifts = {node: True for node in nodes}
    loads = _force_lines(form, nodes, "load", load_shifts, settings)
    shifts = reaction_shifts(form, nodes)
    reactions = _force_lines(form, nodes, "support_force", shifts, settings)

    labels = []
    if settings.show_labels:
        labels = [_force_label(form, edge) for edge in edges]

    drawing = FormDrawing(
        nodes=node_points,
        support_nodes=support_points,
        edges=edge_lines,
        loads=loads,
        reactions=reactions,
        labels=labels,
    )

    return drawing


def edge_widths(form, width_min, width_max):
    """
    The width to draw every edge of a form diagram with.

    Parameters
    ----------
    form :
        The form diagram.
    width_min :
        The width of the edge with the smallest absolute force.
    width_max :
        The width of the edge with the largest absolute force.

    Returns
    -------
    widths :
        A mapping of every edge to its width.

    Notes
    -----
    The absolute edge forces are spread linearly over the width bounds across
    the whole diagram, so a selection keeps the widths it has in the full
    drawing. When every force has the same magnitude, every edge takes the
    largest width, as the plotter does.
    """
    return _spread_by_force(form, width_min, width_max)


def edge_radii(form, radius_min, radius_max):
    """
    The pipe radius to thicken every edge of a form diagram with.

    Parameters
    ----------
    form :
        The form diagram.
    radius_min :
        The radius of the edge with the smallest absolute force.
    radius_max :
        The radius of the edge with the largest absolute force.

    Returns
    -------
    radii :
        A mapping of every edge to its radius.

    Notes
    -----
    The radii follow the same linear spread over the absolute edge forces as
    the widths do.
    """
    return _spread_by_force(form, radius_min, radius_max)


def _spread_by_force(form, value_min, value_max):
    """
    Spread two bounds linearly over the absolute edge forces of a diagram.
    """
    forces = {edge: fabs(form.edge_force(edge)) for edge in form.edges()}
    force_low = min(forces.values())
    force_high = max(forces.values())
    force_range = force_high - force_low

    values = {}
    for edge, force in forces.items():
        ratio = 1.0
        if force_range > 0.0:
            ratio = (force - force_low) / force_range
        values[edge] = (1.0 - ratio) * value_min + ratio * value_max

    return values


def reaction_shifts(form, nodes):
    """
    Whether the reaction force at every node points back into its trail.

    Parameters
    ----------
    form :
        The form diagram.
    nodes :
        The nodes to decide the shift of.

    Returns
    -------
    shifts :
        A mapping of nodes to whether the reaction force is shifted.

    Notes
    -----
    A reaction is shifted when the strongest edge meeting the node is in
    compression, so the force reads as pushing against the support rather
    than pulling away from it. A node with no connected edge is never
    shifted, which also keeps the strongest-edge search off an empty set.

    TODO: needs a more robust check for orientation. What is wanted is to
    know whether the force needs a full shift.
    """
    shifts = {}
    for node in nodes:
        forces = [form.edge_force(edge) for edge in form.node_connected_edges(node)]
        if not forces:
            shifts[node] = False
            continue
        shifts[node] = max(forces, key=fabs) < 0.0

    return shifts


def _styled_node(form, node, radius):
    """
    Style a node, colored by whether it is a support.
    """
    color_name = "node_support" if form.is_node_support(node) else "node"
    point = form.node_coordinates(node)

    return StyledPoint(point=point, color=COLORS[color_name], radius=radius)


def _styled_edge(form, edge, width, radius):
    """
    Style an edge, colored by the sign of its force.
    """
    force = form.edge_force(edge)
    color_name = "edge"
    if force < 0.0:
        color_name = "compression"
    elif force > 0.0:
        color_name = "tension"

    u, v = edge
    start = form.node_coordinates(u)
    end = form.node_coordinates(v)

    return StyledLine(
        start=start,
        end=end,
        color=COLORS[color_name],
        width=width,
        radius=radius,
        is_arrow=False,
    )


def _force_lines(form, nodes, color_name, shifts, settings):
    """
    Style the loads or the reaction forces at a selection of nodes as arrows.

    Parameters
    ----------
    form :
        The form diagram.
    nodes :
        The nodes to draw a force at.
    color_name :
        The scheme color of the forces, `"load"` or `"support_force"`, which
        also picks the node attributes to read.
    shifts :
        A mapping of nodes to whether the arrow ends at the node rather than
        starting at it.
    settings :
        The display settings.

    Returns
    -------
    lines :
        One arrow per force at least as large as the smallest force to draw.

    Notes
    -----
    The arrows are drawn halfway between the edge width bounds, so they stay
    readable next to the edges without following any one force. Thickened,
    their shaft radius is `ARROW_BODYWIDTH` of their length, as jax_fdm
    draws them, and they move along their own direction by the radius of the
    node spheres: back when they end at the node, ahead when they start at it,
    so neither end hides inside the sphere.
    """
    names = ["qx", "qy", "qz"] if color_name == "load" else ["rx", "ry", "rz"]
    width = 0.5 * (settings.width_min + settings.width_max)
    clearance = settings.radius_max

    lines = []
    for node in nodes:
        vector = form.node_attributes(node, names)
        if length_vector(vector) < settings.force_min:
            continue

        scaled = scale_vector(vector, settings.force_scale)
        point = form.node_coordinates(node)
        start = point
        end = add_vectors(point, scaled)
        offset = clearance
        if shifts[node]:
            start = subtract_vectors(point, scaled)
            end = point
            offset = -clearance
        radius = ARROW_BODYWIDTH * length_vector(scaled)

        line = StyledLine(
            start=start,
            end=end,
            color=COLORS[color_name],
            width=width,
            radius=radius,
            is_arrow=True,
            offset=offset,
        )
        lines.append(line)

    return lines


def _force_label(form, edge):
    """
    Label an edge with its force at its midpoint.
    """
    u, v = edge
    start = form.node_coordinates(u)
    end = form.node_coordinates(v)
    point = midpoint_point_point(start, end)
    text = "{:.2f}".format(form.edge_force(edge))

    return TextLabel(point=point, text=text)
