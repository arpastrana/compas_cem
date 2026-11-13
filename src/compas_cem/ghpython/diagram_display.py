"""
The style rules for drawing form and topology diagrams in Grasshopper, kept
free of Rhino.
"""

from dataclasses import dataclass
from math import fabs
from math import sqrt
from typing import NamedTuple

from compas.geometry import add_vectors
from compas.geometry import distance_point_point
from compas.geometry import length_vector
from compas.geometry import midpoint_point_point
from compas.geometry import scale_vector
from compas.geometry import subtract_vectors

from compas_cem import ARROW_BODYWIDTH
from compas_cem import COLORS
from compas_cem import LOAD_CROSS_SIZE

__all__ = [
    "FormDisplaySettings",
    "FormDrawing",
    "StyledLine",
    "StyledPoint",
    "StyledPolyline",
    "TextLabel",
    "TopologyDrawing",
    "cross_lines",
    "edge_radii",
    "edge_widths",
    "form_drawing",
    "reaction_shifts",
    "topology_drawing",
]

# The pixel width of every topology edge, trail and load cross.
TOPOLOGY_WIDTH = 2.0
# Free nodes are light gray rather than white, so they show against a white background.
NODE_TINT = (200, 200, 200)


@dataclass(frozen=True)
class FormDisplaySettings:
    """
    The settings to draw a form diagram with in Grasshopper.

    Parameters
    ----------
    arrow_min :
        The smallest load or reaction magnitude to draw as an arrow, or the
        smallest component when the forces are decomposed. It is compared
        before `arrow_scale` applies, so the scale never hides an arrow.
    arrow_scale :
        The factor that turns a load or reaction force into its arrow length.
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
    thick_sides :
        The number of faces around every thickened pipe, arrow and node sphere.
    show_loads :
        Whether to draw the loads.
    show_reactions :
        Whether to draw the reaction forces.
    show_forces :
        Whether to label every drawn edge with its force.
    show_keys :
        Whether to label every drawn node and edge with its key.
    decompose :
        Whether to draw every load and reaction force as its x, y and z
        components, an arrow each, rather than as one arrow.

    Notes
    -----
    The settings are a dataclass rather than a named tuple, because Grasshopper
    unpacks a tuple output into its items. Draw Form sets `decompose` and the
    visibility toggles from its own inputs.
    """

    arrow_min: float = 1e-3
    arrow_scale: float = 1.0
    width_min: float = 1.0
    width_max: float = 8.0
    radius_min: float = 0.01
    radius_max: float = 0.1
    thick_sides: int = 8
    show_loads: bool = True
    show_reactions: bool = True
    show_forces: bool = False
    show_keys: bool = False
    decompose: bool = True

    def __post_init__(self):
        bounds = {
            "width": (self.width_min, self.width_max),
            "radius": (self.radius_min, self.radius_max),
        }
        for name, (low, high) in bounds.items():
            if not 0.0 < low <= high:
                template = "The edge {0}s need 0 < {0}_min <= {0}_max, got {1} and {2}."
                message = template.format(name, low, high)
                raise ValueError(message)
        if self.thick_sides < 3:
            template = "A thickened mesh needs at least 3 sides, got {}."
            message = template.format(self.thick_sides)
            raise ValueError(message)


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
    model units, whether it ends in an arrowhead, how far a thickened arrow
    moves along its own direction to clear the sphere of its node, whether it
    is dashed, and how far a thickened pipe stops short of each end.
    """

    start: list[float]
    end: list[float]
    color: tuple[int, int, int]
    width: float
    radius: float
    is_arrow: bool
    offset: float = 0.0
    is_dashed: bool = False
    trim: float = 0.0


class StyledPolyline(NamedTuple):
    """
    A polyline to draw, with its color and its width in pixels.
    """

    points: list[list[float]]
    color: tuple[int, int, int]
    width: float


class TextLabel(NamedTuple):
    """
    A text to draw at a point.
    """

    point: list[float]
    text: str


class TopologyDrawing(NamedTuple):
    """
    A topology diagram styled for drawing.
    """

    nodes: list[StyledPoint]
    origin_nodes: list[StyledPoint]
    support_nodes: list[StyledPoint]
    edges: list[StyledLine]
    trail_edges: list[StyledLine]
    deviation_edges: list[StyledLine]
    trails: list[StyledPolyline]
    loads: list[StyledLine]
    labels: list[TextLabel]


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
        labels. A category the settings hide is empty.

    Notes
    -----
    Every node is colored by whether it is a support, so the support nodes are
    drawn twice, once among the nodes and once on their own. A load arrow
    always ends at its node, so its head touches the node it loads; a reaction
    ends at its support only when it pushes into it. An edge shown with both
    its key and its force gets one label, `u-v: force`, so the two never
    overlap.
    """
    nodes = list(form.nodes()) if node_keys is None else list(node_keys)
    edges = list(form.edges()) if edge_keys is None else list(edge_keys)
    supports = [node for node in nodes if form.is_node_support(node)]

    sphere_radius = settings.radius_max
    node_points = [_styled_node(form, node, sphere_radius) for node in nodes]
    support_points = [_styled_node(form, node, sphere_radius) for node in supports]

    ratios = _force_ratios(form)
    widths = _spread_ratios(ratios, settings.width_min, settings.width_max)
    radii = _spread_ratios(ratios, settings.radius_min, settings.radius_max)
    edge_lines = []
    for edge in edges:
        key = tuple(edge)
        line = _styled_edge(form, edge, widths[key], radii[key], sphere_radius)
        edge_lines.append(line)

    loads = []
    if settings.show_loads:
        load_shifts = {node: True for node in nodes}
        loads = _force_lines(form, nodes, "load", load_shifts, settings)

    reactions = []
    if settings.show_reactions:
        shifts = reaction_shifts(form, nodes)
        reactions = _force_lines(form, nodes, "support_force", shifts, settings)

    labels = _form_labels(form, nodes, edges, settings)

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
    ratios = _force_ratios(form)
    widths = _spread_ratios(ratios, width_min, width_max)

    return widths


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
    ratios = _force_ratios(form)
    radii = _spread_ratios(ratios, radius_min, radius_max)

    return radii


def _force_ratios(form):
    """
    Where the absolute force of every edge lies between the smallest and the
    largest, from zero to one, or one everywhere if they are all equal.
    """
    forces = {edge: fabs(form.edge_force(edge)) for edge in form.edges()}
    if not forces:
        return {}

    force_low = min(forces.values())
    force_high = max(forces.values())
    force_range = force_high - force_low

    ratios = {}
    for edge, force in forces.items():
        ratio = 1.0
        if force_range > 0.0:
            ratio = (force - force_low) / force_range
        ratios[edge] = ratio

    return ratios


def _spread_ratios(ratios, value_min, value_max):
    """
    Spread two bounds linearly over the force ratios of the edges.
    """
    values = {}
    for edge, ratio in ratios.items():
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
    color = COLORS["node_support"] if form.is_node_support(node) else NODE_TINT
    point = form.node_coordinates(node)
    styled_point = StyledPoint(point=point, color=color, radius=radius)

    return styled_point


def _styled_edge(form, edge, width, radius, sphere_radius):
    """
    Style an edge, colored by the sign of its force, whose thickened pipe stops
    one sphere radius short of each end node.

    Notes
    -----
    A sphere is meshed with flat faces inside its true surface, so a pipe whose
    rim met the true sphere would poke through the mesh; one full sphere radius
    keeps every pipe outside it.
    """
    trim = sphere_radius
    force = form.edge_force(edge)
    color_name = "edge"
    if force < 0.0:
        color_name = "compression"
    elif force > 0.0:
        color_name = "tension"

    u, v = edge
    start = form.node_coordinates(u)
    end = form.node_coordinates(v)
    styled_line = StyledLine(
        start=start,
        end=end,
        color=COLORS[color_name],
        width=width,
        radius=radius,
        is_arrow=False,
        trim=trim,
    )

    return styled_line


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
    their shaft radius is `ARROW_BODYWIDTH` of their length, and they move
    along their own direction by the radius of the node spheres: back when
    they end at the node, ahead when they start at it, so neither end hides
    inside the sphere. Decomposed, every component at least as large as the
    smallest force to draw gets its own arrow, placed by the same rules.
    """
    names = ["qx", "qy", "qz"] if color_name == "load" else ["rx", "ry", "rz"]
    width = 0.5 * (settings.width_min + settings.width_max)
    clearance = settings.radius_max

    lines = []
    for node in nodes:
        vector = form.node_attributes(node, names)
        point = form.node_coordinates(node)
        for component in _force_components(vector, settings.decompose):
            if length_vector(component) < settings.arrow_min:
                continue

            scaled = scale_vector(component, settings.arrow_scale)
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


def _force_components(vector, decompose):
    """
    The vectors to draw for a force: its x, y and z components when
    decomposed, or the force itself.
    """
    if not decompose:
        return [vector]

    x, y, z = vector
    components = [[x, 0.0, 0.0], [0.0, y, 0.0], [0.0, 0.0, z]]

    return components


def _form_labels(form, nodes, edges, settings):
    """
    Label the nodes with their keys, and the edges with their keys, their
    forces, or both.
    """
    labels = []
    if settings.show_keys:
        labels = _node_labels(form, nodes)

    for edge in edges:
        text_parts = []
        if settings.show_keys:
            key_text = _edge_key(edge)
            text_parts.append(key_text)
        if settings.show_forces:
            force_text = "{:.2f}".format(form.edge_force(edge))
            text_parts.append(force_text)
        if text_parts:
            text = ": ".join(text_parts)
            label = _edge_label(form, edge, text)
            labels.append(label)

    return labels


def topology_drawing(topology, node_keys, edge_keys, show_keys):
    """
    Style a selection of a topology diagram for drawing.

    Parameters
    ----------
    topology :
        The topology diagram to draw.
    node_keys :
        The nodes to draw, with the crosses of the loaded ones. If `None`,
        every node is drawn.
    edge_keys :
        The edges to draw. If `None`, every edge is drawn.
    show_keys :
        Whether to label the drawn nodes and edges with their keys.

    Returns
    -------
    drawing :
        The styled nodes, origin nodes, support nodes, edges, trail edges,
        deviation edges, trails, load crosses, and the key labels when shown.

    Notes
    -----
    The colors follow the topology plotter's defaults: nodes by type, and
    edges by the state their length or force sets, with auxiliary trails
    apart. Deviation edges are always dashed. A loaded node is marked with a
    cross of two lines at right angles in the XY plane, each reaching
    `LOAD_CROSS_SIZE` of the diagram's bounding-box diagonal from the node.
    Every trail is drawn whole, whatever the edge selection.
    """
    nodes = list(topology.nodes()) if node_keys is None else list(node_keys)
    edges = list(topology.edges()) if edge_keys is None else list(edge_keys)

    node_points = [_topology_node(topology, node) for node in nodes]
    node_styles = list(zip(nodes, node_points))
    origin_points = [
        point for node, point in node_styles if topology.is_node_origin(node)
    ]
    support_points = [
        point for node, point in node_styles if topology.is_node_support(node)
    ]

    auxiliary_trails = {tuple(trail) for trail in topology.auxiliary_trails()}
    edge_lines = [_topology_edge(topology, edge, auxiliary_trails) for edge in edges]
    edge_styles = list(zip(edges, edge_lines))
    trail_lines = [line for edge, line in edge_styles if topology.is_trail_edge(edge)]
    deviation_lines = [
        line for edge, line in edge_styles if topology.is_deviation_edge(edge)
    ]
    trails = _topology_trails(topology, auxiliary_trails)

    loaded_nodes = set(topology.loaded_nodes())
    crossed_nodes = [node for node in nodes if node in loaded_nodes]
    crosses = _load_crosses(topology, crossed_nodes)

    labels = []
    if show_keys:
        labels = _key_labels(topology, nodes, edges)

    drawing = TopologyDrawing(
        nodes=node_points,
        origin_nodes=origin_points,
        support_nodes=support_points,
        edges=edge_lines,
        trail_edges=trail_lines,
        deviation_edges=deviation_lines,
        trails=trails,
        loads=crosses,
        labels=labels,
    )

    return drawing


def _topology_node(topology, node):
    """
    Style a topology node, colored by whether it is a support or an origin.
    """
    color = NODE_TINT
    if topology.is_node_support(node):
        color = COLORS["node_support"]
    elif topology.is_node_origin(node):
        color = COLORS["node_origin"]
    point = topology.node_coordinates(node)
    styled_point = StyledPoint(point=point, color=color, radius=0.0)

    return styled_point


def _topology_edge(topology, edge, auxiliary_trails):
    """
    Style a topology edge, colored by its state and dashed if it deviates.

    Notes
    -----
    A trail edge takes its state from the sign of its length and a deviation
    edge from the sign of its force; an edge with neither sign is gray, and an
    auxiliary trail edge orange, as the topology plotter draws them. An
    auxiliary trail has two nodes, so its node tuple names its one edge.
    """
    color_name = "edge"
    if tuple(edge) in auxiliary_trails:
        color_name = "auxiliary_trail"
    else:
        name = "length" if topology.is_trail_edge(edge) else "force"
        value = topology.edge_attribute(edge, name)
        if value:
            color_name = "compression" if value < 0.0 else "tension"

    u, v = edge
    start = topology.node_coordinates(u)
    end = topology.node_coordinates(v)
    is_dashed = topology.is_deviation_edge(edge)
    styled_line = StyledLine(
        start=start,
        end=end,
        color=COLORS[color_name],
        width=TOPOLOGY_WIDTH,
        radius=0.0,
        is_arrow=False,
        is_dashed=is_dashed,
    )

    return styled_line


def _topology_trails(topology, auxiliary_trails):
    """
    Style every trail as a polyline, the auxiliary trails apart.
    """
    polylines = []
    for trail in topology.trails():
        points = [topology.node_coordinates(node) for node in trail]
        is_auxiliary = tuple(trail) in auxiliary_trails
        color_name = "auxiliary_trail" if is_auxiliary else "trail"
        polyline = StyledPolyline(
            points=points,
            color=COLORS[color_name],
            width=TOPOLOGY_WIDTH,
        )
        polylines.append(polyline)

    return polylines


def cross_lines(diagram, nodes):
    """
    The two lines of the cross that marks every given node.

    Parameters
    ----------
    diagram :
        The diagram the nodes belong to, whose extent sizes the crosses.
    nodes :
        The nodes to mark.

    Returns
    -------
    lines :
        Two start and end point pairs per node, at right angles in the XY
        plane, each reaching `LOAD_CROSS_SIZE` of the diagram's bounding-box
        diagonal from the node.

    Notes
    -----
    Every engine that crosses the loaded nodes of a topology draws these lines,
    so the crosses match across them.
    """
    diagonal = _diagram_diagonal(diagram)
    reach = LOAD_CROSS_SIZE * diagonal / sqrt(2.0)

    lines = []
    for node in nodes:
        x, y, z = diagram.node_coordinates(node)
        for sign in (1.0, -1.0):
            start = [x - reach, y - sign * reach, z]
            end = [x + reach, y + sign * reach, z]
            lines.append((start, end))

    return lines


def _load_crosses(topology, nodes):
    """
    Style the cross that marks every loaded node, as two lines each.
    """
    color = COLORS["node_black"]

    crosses = []
    for start, end in cross_lines(topology, nodes):
        line = StyledLine(
            start=start,
            end=end,
            color=color,
            width=TOPOLOGY_WIDTH,
            radius=0.0,
            is_arrow=False,
        )
        crosses.append(line)

    return crosses


def _diagram_diagonal(diagram):
    """
    The length of the diagonal of a diagram's bounding box, or one if it has
    no extent.
    """
    points = [diagram.node_coordinates(node) for node in diagram.nodes()]
    if not points:
        return 1.0

    corner_low = [min(point[axis] for point in points) for axis in range(3)]
    corner_high = [max(point[axis] for point in points) for axis in range(3)]
    diagonal = distance_point_point(corner_low, corner_high)
    if not diagonal:
        return 1.0

    return diagonal


def _key_labels(diagram, nodes, edges):
    """
    Label the nodes with their keys and the edges with `u-v` at their midpoints.
    """
    labels = _node_labels(diagram, nodes)
    for edge in edges:
        text = _edge_key(edge)
        label = _edge_label(diagram, edge, text)
        labels.append(label)

    return labels


def _node_labels(diagram, nodes):
    """
    Label the nodes with their keys at their positions.
    """
    labels = []
    for node in nodes:
        point = diagram.node_coordinates(node)
        text = str(node)
        label = TextLabel(point=point, text=text)
        labels.append(label)

    return labels


def _edge_label(diagram, edge, text):
    """
    Place a text at the midpoint of an edge.
    """
    u, v = edge
    start = diagram.node_coordinates(u)
    end = diagram.node_coordinates(v)
    point = midpoint_point_point(start, end)
    label = TextLabel(point=point, text=text)

    return label


def _edge_key(edge):
    """
    The key of an edge written as `u-v`.
    """
    u, v = edge
    key_text = "{}-{}".format(u, v)

    return key_text
