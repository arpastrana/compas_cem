"""
Build the COMPAS CEM logo from its form-found, self-stressed form diagram.

Every member becomes a band whose width is proportional to its force, red in
tension and blue in compression; no loads or reactions are drawn. Where two
members cross without a node, the upper one cuts a halo of whitespace into the
lower one. Three tiers share these proportions and differ only in weight: the
thin mark for large and vector use, the regular mark for mid sizes, and a bare
icon for 40 px and below.

Run from the repository root:

    uv run --with shapely python scripts/logo/build_logo.py

It writes SVG, PDF and transparent PNG files to docs/assets/logo.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import NamedTuple

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path as MplPath  # noqa: E402
from shapely.geometry import GeometryCollection  # noqa: E402
from shapely.geometry import LinearRing  # noqa: E402
from shapely.geometry import LineString  # noqa: E402
from shapely.geometry import MultiPolygon  # noqa: E402
from shapely.geometry import Polygon  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

from compas_cem import COLORS  # noqa: E402
from compas_cem.diagrams import FormDiagram  # noqa: E402

HERE = Path(__file__).parent
FORM_PATH = HERE / "compas_cem_logo.json"
OUTPUT_FOLDER = HERE.parents[1] / "docs" / "assets" / "logo"

WHITE = (255, 255, 255)
NODE_RIM = (50, 50, 50)
DARK_GROUND = (31, 34, 40)
MITRE = {"join_style": "mitre", "mitre_limit": 5.0}
# The trail-to-triangle corner angle halved, for equilateral triangles.
HALF_ANGLE = math.radians(30.0)


def mix_colors(color, base, amount):
    """
    Mix a color over a base color.

    Parameters
    ----------
    color :
        The color to mix in, as RGB integers.
    base :
        The color underneath, as RGB integers.
    amount :
        The share of `color`, from 0 for the base alone to 1 for the color alone.

    Returns
    -------
    mixed :
        The mixed color as RGB integers.
    """
    pairs = zip(color, base)
    mixed = tuple(round(amount * c + (1.0 - amount) * b) for c, b in pairs)

    return mixed


CELL_LIGHT = mix_colors(COLORS["compression"], WHITE, 0.16)
CELL_DARK = mix_colors(COLORS["compression"], DARK_GROUND, 0.30)


class LogoStyle(NamedTuple):
    """
    The weight and details of one logo tier, in units of the support radius.
    """

    width_scale: float
    cross_gap: float
    cell_gap: float
    node_radius: float
    node_rim: float


class LogoShapes(NamedTuple):
    """
    The filled shapes of a logo, ready to draw.
    """

    tension: Polygon
    compression: MultiPolygon
    cells: list[Polygon]
    nodes: list[tuple[float, float]]


class LogoFile(NamedTuple):
    """
    One file to write: its tier, ground mode, format and pixel size.
    """

    name: str
    tier: str
    mode: str
    size: int


TIERS = {
    "thin": LogoStyle(0.05, 0.028, 0.028, 0.062, 0.018),
    "regular": LogoStyle(0.065, 0.03, 0.03, 0.07, 0.02),
    "icon": LogoStyle(0.12, 0.05, 0.0, 0.0, 0.0),
}

FILES = [
    LogoFile("compas_cem_logo.svg", "thin", "light", 1000),
    LogoFile("compas_cem_logo_dark.svg", "thin", "dark", 1000),
    LogoFile("compas_cem_logo_regular.svg", "regular", "light", 1000),
    LogoFile("compas_cem_logo_regular_dark.svg", "regular", "dark", 1000),
    LogoFile("compas_cem_icon.svg", "icon", "light", 1000),
    LogoFile("compas_cem_logo.pdf", "thin", "light", 1000),
    LogoFile("compas_cem_icon.pdf", "icon", "light", 1000),
    LogoFile("compas_cem_logo_1024.png", "thin", "light", 1024),
    LogoFile("compas_cem_logo_512.png", "thin", "light", 512),
    LogoFile("compas_cem_logo_dark_1024.png", "thin", "dark", 1024),
    LogoFile("compas_cem_logo_dark_512.png", "thin", "dark", 512),
    LogoFile("compas_cem_logo_regular_128.png", "regular", "light", 128),
    LogoFile("compas_cem_logo_regular_dark_128.png", "regular", "dark", 128),
    LogoFile("compas_cem_icon_64.png", "icon", "light", 64),
    LogoFile("compas_cem_icon_32.png", "icon", "light", 32),
    LogoFile("compas_cem_icon_24.png", "icon", "light", 24),
]


def ring_by_angle(form, nodes):
    """
    A closed ring through nodes, sorted by their angle around the origin.

    Parameters
    ----------
    form :
        The form diagram.
    nodes :
        The keys of the nodes on the ring.

    Returns
    -------
    ring :
        The closed ring in the XY plane.
    """
    points = [form.node_coordinates(node)[:2] for node in nodes]
    ordered = sorted(points, key=lambda point: math.atan2(point[1], point[0]))
    ring = LinearRing(ordered)

    return ring


def spoke_band(form, edge, origin_width, style):
    """
    The band of a trail edge, started where its corners meet its triangle.

    Parameters
    ----------
    form :
        The form diagram.
    edge :
        The trail edge, from a triangle corner to a support.
    origin_width :
        The width of the triangle at the trail's origin node.
    style :
        The logo tier.

    Returns
    -------
    band :
        The spoke as a polygon.

    Notes
    -----
    A spoke is wider than its triangle, so a band started at the corner would
    poke out of it. Starting it where its corners touch the triangle's outer
    edges hides the start inside the triangle's mitre.
    """
    u, v = edge
    origin, support = (u, v) if form.node_attribute(v, "type") == "support" else (v, u)
    start = form.node_coordinates(origin)[:2]
    end = form.node_coordinates(support)[:2]
    length = math.hypot(end[0] - start[0], end[1] - start[1])
    direction = ((end[0] - start[0]) / length, (end[1] - start[1]) / length)
    width = style.width_scale * abs(form.edge_force(edge))
    tip = origin_width / 2.0 / math.sin(HALF_ANGLE)
    offset = tip - width / 2.0 / math.tan(HALF_ANGLE)
    shifted = (start[0] + offset * direction[0], start[1] + offset * direction[1])
    line = LineString([shifted, end])
    band = line.buffer(width / 2.0, cap_style="flat")

    return band


def logo_shapes(form, style):
    """
    Turn the form diagram into the filled shapes of one logo tier.

    Parameters
    ----------
    form :
        The form diagram of the logo.
    style :
        The logo tier.

    Returns
    -------
    shapes :
        The tension ring, the compression members, the inset cells and the
        node positions.

    Notes
    -----
    The big triangle passes over the long spokes and the corners of the small
    triangle, so its halo trims both. Cells are what remains inside the ring
    once every member, grown by the cell gap, is taken out.
    """
    edges = list(form.edges())
    tension_edges = [edge for edge in edges if form.edge_force(edge) > 0]
    supports = sorted({node for edge in tension_edges for node in edge})
    ring = ring_by_angle(form, supports)
    ring_width = style.width_scale * form.edge_force(tension_edges[0])
    ring_band = ring.buffer(ring_width / 2.0, **MITRE)

    triangle_edges = [
        edge
        for edge in edges
        if form.edge_attribute(edge, "type") == "deviation"
        and form.edge_force(edge) < 0
    ]
    origins = sorted({node for edge in triangle_edges for node in edge})
    radii = {node: math.hypot(*form.node_coordinates(node)[:2]) for node in origins}
    radius_mid = sum(radii.values()) / len(radii)
    outer_nodes = [node for node in origins if radii[node] > radius_mid]
    inner_nodes = [node for node in origins if radii[node] < radius_mid]

    triangle_widths = {}
    triangles = []
    for corner_nodes in (outer_nodes, inner_nodes):
        corner_set = set(corner_nodes)
        side = next(edge for edge in triangle_edges if set(edge) <= corner_set)
        side_width = style.width_scale * abs(form.edge_force(side))
        triangle_ring = ring_by_angle(form, corner_nodes)
        triangles.append(triangle_ring.buffer(side_width / 2.0, **MITRE))
        triangle_widths.update({node: side_width for node in corner_nodes})
    big_triangle, small_triangle = triangles
    halo = big_triangle.buffer(style.cross_gap, **MITRE)

    trail_edges = [
        edge for edge in edges if form.edge_attribute(edge, "type") == "trail"
    ]
    spokes_full = []
    spokes_drawn = []
    for edge in trail_edges:
        u, v = edge
        origin = u if u in triangle_widths else v
        band = spoke_band(form, edge, triangle_widths[origin], style)
        spokes_full.append(band)
        if origin in inner_nodes:
            band = band.difference(halo)
        spokes_drawn.append(band)

    small_drawn = small_triangle.difference(halo)
    members = unary_union([big_triangle, small_drawn, *spokes_drawn])
    trimmed = members.difference(ring_band)
    pieces = polygon_parts(trimmed)
    compression = MultiPolygon(pieces)

    cells = []
    if style.cell_gap > 0:
        solid = unary_union([ring_band, big_triangle, small_triangle, *spokes_full])
        grown = solid.buffer(style.cell_gap, **MITRE)
        hexagon = Polygon(ring.coords)
        free = hexagon.difference(grown)
        cells = [piece for piece in polygon_parts(free) if piece.area > 1e-4]

    nodes = []
    if style.node_radius > 0:
        nodes = [tuple(form.node_coordinates(node)[:2]) for node in form.nodes()]

    shapes = LogoShapes(ring_band, compression, cells, nodes)

    return shapes


def polygon_parts(geometry) -> list[Polygon]:
    """
    The polygons of a geometry, whatever its type.

    Parameters
    ----------
    geometry :
        A shapely polygon or collection.

    Returns
    -------
    polygons :
        The polygons it holds, empty if none.
    """
    if isinstance(geometry, Polygon):
        polygons = [] if geometry.is_empty else [geometry]
    elif isinstance(geometry, (MultiPolygon, GeometryCollection)):
        polygons = [part for part in geometry.geoms if isinstance(part, Polygon)]
    else:
        message = "Expected polygons, got {}.".format(type(geometry).__name__)
        raise TypeError(message)

    return polygons


def fill_layers(shapes, mode):
    """
    The filled shapes of a logo with their colors, bottom to top.

    Parameters
    ----------
    shapes :
        The logo shapes.
    mode :
        `"light"` or `"dark"`, the ground the logo sits on.

    Returns
    -------
    layers :
        Pairs of a shape and its RGB color.
    """
    cell_color = CELL_LIGHT if mode == "light" else CELL_DARK
    layers = [(cell, cell_color) for cell in shapes.cells]
    layers.append((shapes.tension, COLORS["tension"]))
    layers.append((shapes.compression, COLORS["compression"]))

    return layers


def logo_extent(style):
    """
    The half-width of the square that holds a logo tier, in radius units.

    Parameters
    ----------
    style :
        The logo tier.

    Returns
    -------
    extent :
        The half-width, with room for the ring, its mitres and the nodes.
    """
    ring_reach = 0.6 * style.width_scale * math.sqrt(3.0)
    extent = 1.0 + ring_reach + style.node_radius + 0.02

    return extent


def hex_color(rgb):
    """
    A color as a hex string.

    Parameters
    ----------
    rgb :
        The color as RGB integers.

    Returns
    -------
    text :
        The color as `#rrggbb`.
    """
    text = "#{:02x}{:02x}{:02x}".format(*rgb)

    return text


def svg_path(polygons, scale, offset):
    """
    SVG path data for polygons with holes, with the y axis flipped.

    Parameters
    ----------
    polygons :
        The polygons to trace.
    scale :
        The pixels per radius unit.
    offset :
        The pixel position of the origin on both axes.

    Returns
    -------
    data :
        The path data, one closed subpath per ring.
    """
    subpaths = []
    for polygon in polygons:
        for ring in [polygon.exterior, *polygon.interiors]:
            coords = list(ring.coords)[:-1]
            points = [
                f"{offset + scale * x:.2f} {offset - scale * y:.2f}" for x, y in coords
            ]
            subpath = "M" + " L".join(points) + " Z"
            subpaths.append(subpath)
    data = " ".join(subpaths)

    return data


def svg_document(shapes, style, mode, size):
    """
    A logo as an SVG document with a transparent background.

    Parameters
    ----------
    shapes :
        The logo shapes.
    style :
        The logo tier.
    mode :
        `"light"` or `"dark"`, the ground the logo sits on.
    size :
        The width and height of the view box in pixels.

    Returns
    -------
    document :
        The SVG markup.
    """
    scale = size / (2.0 * logo_extent(style))
    offset = size / 2.0
    elements = []
    for shape, color in fill_layers(shapes, mode):
        parts = polygon_parts(shape)
        data = svg_path(parts, scale, offset)
        element = f'<path fill="{hex_color(color)}" fill-rule="evenodd" d="{data}"/>'
        elements.append(element)

    rim = style.node_rim * scale
    radius = style.node_radius * scale - rim / 2.0
    for x, y in shapes.nodes:
        element = (
            f'<circle cx="{offset + scale * x:.2f}" cy="{offset - scale * y:.2f}" '
            f'r="{radius:.2f}" fill="{hex_color(WHITE)}" '
            f'stroke="{hex_color(NODE_RIM)}" stroke-width="{rim:.2f}"/>'
        )
        elements.append(element)

    header = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'width="{size}" height="{size}">'
    )
    lines = [header, *elements, "</svg>"]
    document = "\n".join(lines) + "\n"

    return document


def draw_figure(shapes, style, mode, size):
    """
    A logo as a matplotlib figure with a transparent background.

    Parameters
    ----------
    shapes :
        The logo shapes.
    style :
        The logo tier.
    mode :
        `"light"` or `"dark"`, the ground the logo sits on.
    size :
        The width and height in pixels at one dot per pixel.

    Returns
    -------
    figure :
        The figure, sized one inch at `size` dots per inch.
    """
    figure = plt.figure(figsize=(1.0, 1.0), dpi=size)
    axes = figure.add_axes((0.0, 0.0, 1.0, 1.0))
    for shape, color in fill_layers(shapes, mode):
        face = [channel / 255.0 for channel in color]
        for polygon in polygon_parts(shape):
            vertices = []
            codes = []
            for ring in [polygon.exterior, *polygon.interiors]:
                coords = list(ring.coords)
                vertices.extend(coords)
                ring_codes = [MplPath.MOVETO] + [MplPath.LINETO] * (len(coords) - 2)
                codes.extend(ring_codes + [MplPath.CLOSEPOLY])
            path = MplPath(vertices, codes)
            patch = PathPatch(path, facecolor=face, edgecolor="none", linewidth=0.0)
            axes.add_patch(patch)

    rim_color = [channel / 255.0 for channel in NODE_RIM]
    for center in shapes.nodes:
        outer = Circle(center, style.node_radius, color=rim_color, linewidth=0.0)
        inner = Circle(
            center, style.node_radius - style.node_rim, color="white", linewidth=0.0
        )
        axes.add_patch(outer)
        axes.add_patch(inner)

    extent = logo_extent(style)
    axes.set_xlim(-extent, extent)
    axes.set_ylim(-extent, extent)
    axes.set_aspect("equal")
    axes.axis("off")

    return figure


def write_logo(form, logo_file):
    """
    Write one logo file in the format its name gives.

    Parameters
    ----------
    form :
        The form diagram of the logo.
    logo_file :
        The file to write.
    """
    style = TIERS[logo_file.tier]
    shapes = logo_shapes(form, style)
    path = OUTPUT_FOLDER / logo_file.name
    if path.suffix == ".svg":
        document = svg_document(shapes, style, logo_file.mode, logo_file.size)
        path.write_text(document)
        return

    figure = draw_figure(shapes, style, logo_file.mode, logo_file.size)
    figure.savefig(path, dpi=logo_file.size, transparent=True)
    plt.close(figure)


def main():
    """
    Write every logo file.
    """
    form = FormDiagram.from_json(FORM_PATH)
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    for logo_file in FILES:
        write_logo(form, logo_file)
        print(OUTPUT_FOLDER / logo_file.name)


if __name__ == "__main__":
    main()
