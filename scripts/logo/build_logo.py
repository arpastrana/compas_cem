"""
Build the COMPAS CEM logo from its form-found, self-stressed form diagram.

Every member becomes a band whose width is proportional to its force; no loads
or reactions are drawn. Where two members cross without a node, the upper one
cuts a gap into the lower one. The logo is white on the blue of the COMPAS
logo: the tension hexagon in a lighter tone, the compression members and the
nodes solid. Two tiers share these proportions, a regular weight for 26 px and
up and a heavier one below, where thin lines fade. Away from the blue docs
header, the logo sits on a blue rounded tile.

Run from the repository root:

    uv run --with shapely python scripts/logo/build_logo.py

It writes SVG, PDF and PNG files to docs/assets/logo, and the Rhino package
icon to the yak template.
"""

from __future__ import annotations

import math
import shutil
from pathlib import Path
from typing import NamedTuple

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path as MplPath  # noqa: E402
from shapely.geometry import GeometryCollection  # noqa: E402
from shapely.geometry import LinearRing  # noqa: E402
from shapely.geometry import LineString  # noqa: E402
from shapely.geometry import MultiPolygon  # noqa: E402
from shapely.geometry import Point  # noqa: E402
from shapely.geometry import Polygon  # noqa: E402
from shapely.geometry.base import BaseGeometry  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

from compas_cem.diagrams import FormDiagram  # noqa: E402

HERE = Path(__file__).parent
FORM_PATH = HERE / "compas_cem_logo.json"
OUTPUT_FOLDER = HERE.parents[1] / "docs" / "assets" / "logo"
YAK_FOLDER = HERE.parents[1] / "src" / "compas_cem" / "ghpython" / "yak_template"

MITRE = {"join_style": "mitre", "mitre_limit": 5.0}
# The trail-to-triangle corner angle halved, for equilateral triangles.
HALF_ANGLE = math.radians(30.0)
# The blue of the COMPAS logo, also the docs header's in docs/assets/css/custom.css.
BLUE = (0, 146, 210)
# The tension hexagon's share of white over the blue.
RING_TONE = 0.65
# A tile leaves a tenth of the logo's width around it, its corners rounded by a fifth.
TILE_MARGIN = 1.1
TILE_ROUNDING = 0.2


class LogoStyle(NamedTuple):
    """
    The weight of one logo tier, in units of the support radius.
    """

    width_scale: float
    cross_gap: float
    node_radius: float


class LogoShapes(NamedTuple):
    """
    The filled members of a logo and the positions of its nodes.
    """

    tension: Polygon
    compression: MultiPolygon
    nodes: list[tuple[float, float]]


class LogoLayers(NamedTuple):
    """
    The two tones of a logo: the tension hexagon, and everything drawn solid.
    """

    ring: BaseGeometry
    solid: BaseGeometry


class LogoFile(NamedTuple):
    """
    One file to write: its tier, its pixel size, and whether it sits on a blue
    tile instead of a transparent background. Its name sets the format.
    """

    name: str
    tier: str
    size: int
    has_tile: bool


TIERS = {
    "regular": LogoStyle(0.065, 0.035, 0.12),
    "small": LogoStyle(0.12, 0.065, 0.155),
}

FILES = [
    LogoFile("compas_cem_logo.svg", "regular", 1000, True),
    LogoFile("compas_cem_logo.pdf", "regular", 1000, True),
    LogoFile("compas_cem_logo_1024.png", "regular", 1024, True),
    LogoFile("compas_cem_logo_512.png", "regular", 512, True),
    LogoFile("compas_cem_logo_128.png", "regular", 128, True),
    LogoFile("compas_cem_logo_small.svg", "small", 1000, True),
    LogoFile("compas_cem_logo_small_64.png", "small", 64, True),
    LogoFile("compas_cem_glyph.svg", "regular", 1000, False),
    LogoFile("compas_cem_glyph_small.pdf", "small", 1000, False),
]
# The Rhino Package Manager shows this file as the package icon.
PACKAGE_ICON = "compas_cem_logo_128.png"


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
    Turn the form diagram into the filled members and nodes of one logo tier.

    Parameters
    ----------
    form :
        The form diagram of the logo.
    style :
        The logo tier.

    Returns
    -------
    shapes :
        The tension hexagon, the compression members and the node positions.

    Notes
    -----
    The big triangle passes over the long spokes and the corners of the small
    triangle, so its gap trims both. The nodes are the supports and the big
    triangle's corners; the small triangle's corners would merge into one dot
    at icon sizes.
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
    spokes = []
    for edge in trail_edges:
        u, v = edge
        origin = u if u in triangle_widths else v
        band = spoke_band(form, edge, triangle_widths[origin], style)
        if origin in inner_nodes:
            band = band.difference(halo)
        spokes.append(band)

    small_drawn = small_triangle.difference(halo)
    members = unary_union([big_triangle, small_drawn, *spokes])
    trimmed = members.difference(ring_band)
    pieces = polygon_parts(trimmed)
    compression = MultiPolygon(pieces)

    node_keys = [*supports, *outer_nodes]
    nodes = [tuple(form.node_coordinates(node)[:2]) for node in node_keys]
    shapes = LogoShapes(ring_band, compression, nodes)

    return shapes


def logo_layers(shapes, style):
    """
    Split a logo into its two tones.

    Parameters
    ----------
    shapes :
        The logo shapes.
    style :
        The logo tier, which sets the node radius.

    Returns
    -------
    layers :
        The tension hexagon without its nodes, drawn in the lighter tone, and
        the compression members with every node, drawn solid.

    Notes
    -----
    The two layers do not overlap, so a node on the hexagon shows solid and no
    see-through area is drawn twice.
    """
    dots = [Point(xy).buffer(style.node_radius, resolution=16) for xy in shapes.nodes]
    nodes = unary_union(dots)
    ring = shapes.tension.difference(nodes)
    pieces = [shapes.compression, nodes]
    solid = unary_union(pieces)
    layers = LogoLayers(ring, solid)

    return layers


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


def canvas_extent(layers, logo_file):
    """
    The half-width of a logo file's canvas, in radius units.

    Parameters
    ----------
    layers :
        The logo layers.
    logo_file :
        The file to write.

    Returns
    -------
    extent :
        The logo's own half-width, widened by the margin of a tile.

    Notes
    -----
    The canvas fits the logo tightly, so a file without a tile fills its slot.
    """
    pieces = [layers.ring, layers.solid]
    whole = unary_union(pieces)
    bounds = [abs(value) for value in whole.bounds]
    extent = max(bounds)
    if logo_file.has_tile:
        extent = TILE_MARGIN * extent

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


def svg_document(layers, logo_file):
    """
    A logo as an SVG document, on a transparent background or a blue tile.

    Parameters
    ----------
    layers :
        The logo layers.
    logo_file :
        The file the document is for, which sets its view box size and tile.

    Returns
    -------
    document :
        The SVG markup.
    """
    size = logo_file.size
    extent = canvas_extent(layers, logo_file)
    scale = size / (2.0 * extent)
    offset = size / 2.0
    elements = []
    if logo_file.has_tile:
        corner = TILE_ROUNDING * extent * scale
        fill = hex_color(BLUE)
        tile = f'<rect width="{size}" height="{size}" rx="{corner:.2f}" fill="{fill}"/>'
        elements.append(tile)

    tones = [(layers.ring, RING_TONE), (layers.solid, 1.0)]
    for shape, tone in tones:
        parts = polygon_parts(shape)
        data = svg_path(parts, scale, offset)
        element = (
            f'<path fill="#ffffff" fill-opacity="{tone:g}" fill-rule="evenodd" '
            f'd="{data}"/>'
        )
        elements.append(element)

    header = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'width="{size}" height="{size}">'
    )
    lines = [header, *elements, "</svg>"]
    document = "\n".join(lines) + "\n"

    return document


def polygon_path(polygon):
    """
    A polygon with holes as a matplotlib path.

    Parameters
    ----------
    polygon :
        The polygon to trace.

    Returns
    -------
    path :
        The path, one closed subpath per ring.
    """
    vertices = []
    codes = []
    for ring in [polygon.exterior, *polygon.interiors]:
        coords = list(ring.coords)
        vertices.extend(coords)
        ring_codes = [MplPath.MOVETO] + [MplPath.LINETO] * (len(coords) - 2)
        codes.extend(ring_codes + [MplPath.CLOSEPOLY])
    path = MplPath(vertices, codes)

    return path


def tile_patch(extent, color):
    """
    The rounded tile a logo sits on.

    Parameters
    ----------
    extent :
        The half-width of the tile, in radius units.
    color :
        The fill, as a matplotlib color.

    Returns
    -------
    patch :
        The tile, its corners rounded by the tile rounding.
    """
    corner = f"round,pad=0,rounding_size={TILE_ROUNDING * extent}"
    origin = (-extent, -extent)
    patch = FancyBboxPatch(
        origin,
        2.0 * extent,
        2.0 * extent,
        boxstyle=corner,
        facecolor=color,
        edgecolor="none",
    )

    return patch


def draw_figure(layers, logo_file):
    """
    A logo as a matplotlib figure, on a transparent background or a blue tile.

    Parameters
    ----------
    layers :
        The logo layers.
    logo_file :
        The file the figure is for, which sets its pixel size and tile.

    Returns
    -------
    figure :
        The figure, sized one inch at the file's pixel size in dots per inch.
    """
    figure = plt.figure(figsize=(1.0, 1.0), dpi=logo_file.size)
    axes = figure.add_axes((0.0, 0.0, 1.0, 1.0))
    extent = canvas_extent(layers, logo_file)
    if logo_file.has_tile:
        face = [channel / 255.0 for channel in BLUE]
        tile = tile_patch(extent, face)
        axes.add_patch(tile)

    tones = [(layers.ring, RING_TONE), (layers.solid, 1.0)]
    for shape, tone in tones:
        for polygon in polygon_parts(shape):
            path = polygon_path(polygon)
            patch = PathPatch(
                path, facecolor="white", alpha=tone, edgecolor="none", linewidth=0.0
            )
            axes.add_patch(patch)

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
    layers = logo_layers(shapes, style)
    path = OUTPUT_FOLDER / logo_file.name
    if path.suffix == ".svg":
        document = svg_document(layers, logo_file)
        path.write_text(document)
        return

    figure = draw_figure(layers, logo_file)
    # A PDF carries no creation date, so rebuilding an unchanged logo changes no file.
    metadata = {"CreationDate": None} if path.suffix == ".pdf" else None
    figure.savefig(path, dpi=logo_file.size, transparent=True, metadata=metadata)
    plt.close(figure)


def main():
    """
    Write every logo file and the Rhino package icon.
    """
    form = FormDiagram.from_json(FORM_PATH)
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    for logo_file in FILES:
        write_logo(form, logo_file)
        print(OUTPUT_FOLDER / logo_file.name)

    package_icon = OUTPUT_FOLDER / PACKAGE_ICON
    yak_icon = YAK_FOLDER / "icon.png"
    shutil.copyfile(package_icon, yak_icon)
    print(yak_icon)


if __name__ == "__main__":
    main()
