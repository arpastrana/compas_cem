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

from compas_cem import COLORS

__all__ = [
    "FormDisplaySettings",
    "FormDrawing",
    "StyledLine",
    "StyledPoint",
    "TextLabel",
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
    show_labels: bool = False

    def __post_init__(self):
        if not 0.0 < self.width_min <= self.width_max:
            message = "The edge widths need 0 < width_min <= width_max, got {} and {}."
            raise ValueError(message.format(self.width_min, self.width_max))


class StyledPoint(NamedTuple):
    """
    A point to draw, with its color.
    """

    point: list[float]
    color: tuple[int, int, int]


class StyledLine(NamedTuple):
    """
    A line to draw, with its color, its width in pixels and whether it ends in an
    arrowhead.
    """

    start: list[float]
    end: list[float]
    color: tuple[int, int, int]
    width: float
    is_arrow: bool


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
    drawn twice, once among the nodes and once on their own.
    """
    nodes = list(form.nodes()) if node_keys is None else list(node_keys)
    edges = list(form.edges()) if edge_keys is None else list(edge_keys)
    supports = [node for node in nodes if form.is_node_support(node)]

    node_points = [_styled_node(form, node) for node in nodes]
    support_points = [_styled_node(form, node) for node in supports]

    widths = edge_widths(form, settings.width_min, settings.width_max)
    edge_lines = [_styled_edge(form, edge, widths[tuple(edge)]) for edge in edges]

    no_shifts = {node: False for node in nodes}
    loads = _force_lines(form, nodes, "load", no_shifts, settings)
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
    forces = {edge: fabs(form.edge_force(edge)) for edge in form.edges()}
    force_low = min(forces.values())
    force_high = max(forces.values())
    force_range = force_high - force_low

    widths = {}
    for edge, force in forces.items():
        ratio = 1.0
        if force_range > 0.0:
            ratio = (force - force_low) / force_range
        widths[edge] = (1.0 - ratio) * width_min + ratio * width_max

    return widths


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


def _styled_node(form, node):
    """
    Style a node, colored by whether it is a support.
    """
    color_name = "node_support" if form.is_node_support(node) else "node"
    point = form.node_coordinates(node)

    return StyledPoint(point=point, color=COLORS[color_name])


def _styled_edge(form, edge, width):
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
    readable next to the edges without following any one force.
    """
    names = ["qx", "qy", "qz"] if color_name == "load" else ["rx", "ry", "rz"]
    width = 0.5 * (settings.width_min + settings.width_max)

    lines = []
    for node in nodes:
        vector = form.node_attributes(node, names)
        if length_vector(vector) < settings.force_min:
            continue

        scaled = scale_vector(vector, settings.force_scale)
        point = form.node_coordinates(node)
        start = point
        end = add_vectors(point, scaled)
        if shifts[node]:
            start = subtract_vectors(point, scaled)
            end = point

        line = StyledLine(
            start=start,
            end=end,
            color=COLORS[color_name],
            width=width,
            is_arrow=True,
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
