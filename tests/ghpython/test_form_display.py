import pytest

from compas.geometry import distance_point_point
from compas.geometry import subtract_vectors

from compas_cem import ARROW_BODYWIDTH
from compas_cem import COLORS
from compas_cem.equilibrium import static_equilibrium
from compas_cem.ghpython import FormDisplaySettings
from compas_cem.ghpython import edge_widths
from compas_cem.ghpython import form_drawing
from compas_cem.ghpython.diagram_display import NODE_TINT

# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def strut_form(compression_strut):
    """
    The form of a one-edge compression strut, supported at node 0, loaded at node 1.
    """
    compression_strut.build_trails()
    return static_equilibrium(compression_strut)


@pytest.fixture
def chain_form(tension_chain):
    """
    The form of a three-edge tension chain, supported at node 3, loaded at node 0.
    """
    tension_chain.build_trails()
    return static_equilibrium(tension_chain)


# ==============================================================================
# Settings
# ==============================================================================


def test_settings_defaults():
    """
    Checks the default display settings, forces shown and labels off.
    """
    settings = FormDisplaySettings()

    assert settings.force_min == 1e-3
    assert settings.arrow_scale == 1.0
    assert settings.width_min == 1.0
    assert settings.width_max == 8.0
    assert settings.radius_min == 0.01
    assert settings.radius_max == 0.1
    assert settings.show_loads is True
    assert settings.show_reactions is True
    assert settings.show_labels is False
    assert settings.decompose is True
    assert settings.thick_sides == 8


@pytest.mark.parametrize("width_min, width_max", [(5.0, 2.0), (0.0, 2.0), (-1.0, 2.0)])
def test_settings_reject_bad_widths(width_min, width_max):
    """
    Checks that the width bounds must be positive and ordered.
    """
    with pytest.raises(ValueError, match="width_min"):
        FormDisplaySettings(width_min=width_min, width_max=width_max)


@pytest.mark.parametrize(
    "radius_min, radius_max", [(0.5, 0.2), (0.0, 0.2), (-0.1, 0.2)]
)
def test_settings_reject_bad_radii(radius_min, radius_max):
    """
    Checks that the radius bounds must be positive and ordered.
    """
    with pytest.raises(ValueError, match="radius_min"):
        FormDisplaySettings(radius_min=radius_min, radius_max=radius_max)


# ==============================================================================
# Edges
# ==============================================================================


def test_edge_colors_follow_force_sign(strut_form, chain_form):
    """
    Checks that compression edges are blue and tension edges are red.
    """
    settings = FormDisplaySettings()
    strut = form_drawing(strut_form, None, None, settings)
    chain = form_drawing(chain_form, None, None, settings)

    assert [line.color for line in strut.edges] == [COLORS["compression"]]
    assert {line.color for line in chain.edges} == {COLORS["tension"]}


def test_edge_widths_spread_by_force(chain_form):
    """
    Checks that the widths spread linearly over the absolute edge forces.
    """
    forces = {(0, 1): 1.0, (1, 2): -3.0, (2, 3): 2.0}
    for edge, force in forces.items():
        chain_form.edge_attribute(edge, "force", force)

    widths = edge_widths(chain_form, 1.0, 5.0)

    assert widths[(0, 1)] == pytest.approx(1.0)
    assert widths[(1, 2)] == pytest.approx(5.0)
    assert widths[(2, 3)] == pytest.approx(3.0)


def test_edge_radii_spread_by_force(chain_form):
    """
    Checks that the pipe radii spread over the forces as the widths do.
    """
    forces = {(0, 1): 1.0, (1, 2): -3.0, (2, 3): 2.0}
    for edge, force in forces.items():
        chain_form.edge_attribute(edge, "force", force)
    settings = FormDisplaySettings(radius_min=0.1, radius_max=0.5)

    drawing = form_drawing(chain_form, None, None, settings)
    radii = [line.radius for line in drawing.edges]

    assert radii == [pytest.approx(0.1), pytest.approx(0.5), pytest.approx(0.3)]


def test_edge_widths_equal_forces(chain_form):
    """
    Checks that edges of equal force magnitude all take the largest width.
    """
    widths = edge_widths(chain_form, 1.0, 5.0)

    assert set(widths.values()) == {5.0}


def test_edge_selection_keeps_full_widths(chain_form):
    """
    Checks that a selected edge keeps the width it has in the full drawing.
    """
    forces = {(0, 1): 1.0, (1, 2): -3.0, (2, 3): 2.0}
    for edge, force in forces.items():
        chain_form.edge_attribute(edge, "force", force)
    settings = FormDisplaySettings(width_min=1.0, width_max=5.0)

    drawing = form_drawing(chain_form, None, [(2, 3)], settings)

    assert [line.width for line in drawing.edges] == [pytest.approx(3.0)]


# ==============================================================================
# Nodes
# ==============================================================================


def test_support_nodes_are_green(strut_form):
    """
    Checks that support nodes are green, both among the nodes and on their own.
    """
    drawing = form_drawing(strut_form, None, None, FormDisplaySettings())
    colors = [point.color for point in drawing.nodes]

    assert colors == [COLORS["node_support"], NODE_TINT]
    assert [point.color for point in drawing.support_nodes] == [COLORS["node_support"]]


def test_node_selection(strut_form):
    """
    Checks that the node selection narrows the nodes, supports, loads and reactions.
    """
    drawing = form_drawing(strut_form, [1], None, FormDisplaySettings())

    assert len(drawing.nodes) == 1
    assert drawing.support_nodes == []
    assert len(drawing.loads) == 1
    assert drawing.reactions == []
    assert len(drawing.edges) == 1


# ==============================================================================
# Forces
# ==============================================================================


@pytest.mark.parametrize("form_name, node", [("strut_form", 1), ("chain_form", 0)])
def test_load_arrow_ends_at_node(form_name, node, request):
    """
    Checks that a load arrow follows the scaled load and ends at its node,
    whatever the force in its edges.
    """
    form = request.getfixturevalue(form_name)
    settings = FormDisplaySettings(arrow_scale=2.0)
    drawing = form_drawing(form, None, None, settings)
    (load,) = drawing.loads
    node_xyz = form.node_coordinates(node)
    scaled = [2.0 * value for value in form.node_load(node)]

    assert load.start == pytest.approx(subtract_vectors(node_xyz, scaled))
    assert load.end == pytest.approx(node_xyz)
    assert load.color == COLORS["load"]
    assert load.is_arrow


def test_reaction_shifted_in_compression(strut_form):
    """
    Checks that a reaction under a compression edge ends at its support.
    """
    drawing = form_drawing(strut_form, None, None, FormDisplaySettings())
    (reaction,) = drawing.reactions

    assert reaction.end == pytest.approx(strut_form.node_coordinates(0))
    assert reaction.color == COLORS["support_force"]


def test_reaction_unshifted_in_tension(chain_form):
    """
    Checks that a reaction under a tension edge starts at its support.
    """
    drawing = form_drawing(chain_form, None, None, FormDisplaySettings())
    (reaction,) = drawing.reactions

    assert reaction.start == pytest.approx(chain_form.node_coordinates(3))


def test_arrows_clear_node_spheres(chain_form):
    """
    Checks that arrows move off their node by the sphere radius: back when they
    end at it, ahead when they start at it.
    """
    settings = FormDisplaySettings(radius_min=0.1, radius_max=0.5)

    drawing = form_drawing(chain_form, None, None, settings)
    (load,) = drawing.loads
    (reaction,) = drawing.reactions

    assert load.offset == pytest.approx(-0.5)
    assert reaction.offset == pytest.approx(0.5)
    assert {point.radius for point in drawing.nodes} == {0.5}


def test_forces_below_minimum_are_skipped(strut_form):
    """
    Checks that loads and reactions smaller than force_min are not drawn.
    """
    settings = FormDisplaySettings(force_min=2.0)
    drawing = form_drawing(strut_form, None, None, settings)

    assert drawing.loads == []
    assert drawing.reactions == []


def test_hidden_loads_keep_reactions(strut_form):
    """
    Checks that hiding the loads empties them and leaves the reactions drawn.
    """
    settings = FormDisplaySettings(show_loads=False)
    drawing = form_drawing(strut_form, None, None, settings)

    assert drawing.loads == []
    assert len(drawing.reactions) == 1


def test_hidden_reactions_keep_loads(strut_form):
    """
    Checks that hiding the reactions empties them and leaves the loads drawn.
    """
    settings = FormDisplaySettings(show_reactions=False)
    drawing = form_drawing(strut_form, None, None, settings)

    assert drawing.reactions == []
    assert len(drawing.loads) == 1


def test_force_arrow_sizes(strut_form):
    """
    Checks that the force arrows sit halfway between the width bounds and that
    their body radius is `ARROW_BODYWIDTH` of their length.
    """
    settings = FormDisplaySettings(width_min=2.0, width_max=6.0, arrow_scale=3.0)
    drawing = form_drawing(strut_form, None, None, settings)
    arrows = drawing.loads + drawing.reactions
    lengths = [distance_point_point(arrow.start, arrow.end) for arrow in arrows]
    radii = [pytest.approx(ARROW_BODYWIDTH * length) for length in lengths]

    assert {arrow.width for arrow in arrows} == {4.0}
    assert [arrow.radius for arrow in arrows] == radii


# ==============================================================================
# Labels
# ==============================================================================


def test_labels_off_by_default(strut_form):
    """
    Checks that no label is drawn unless the settings show them.
    """
    drawing = form_drawing(strut_form, None, None, FormDisplaySettings())

    assert drawing.labels == []


def test_labels_show_edge_forces(strut_form):
    """
    Checks that every drawn edge is labeled with its force at its midpoint.
    """
    settings = FormDisplaySettings(show_labels=True)
    drawing = form_drawing(strut_form, None, None, settings)
    (label,) = drawing.labels
    (edge,) = strut_form.edges()
    force = strut_form.edge_force(edge)
    start = strut_form.node_coordinates(0)
    end = strut_form.node_coordinates(1)
    midpoint = [0.5 * (a + b) for a, b in zip(start, end)]

    assert label.text == "{:.2f}".format(force)
    assert label.point == pytest.approx(midpoint)


# ==============================================================================
# Decomposition
# ==============================================================================


def test_decompose_splits_forces(strut_form):
    """
    Checks that a decomposed load becomes one axis-aligned arrow per nonzero
    component, each ending at the node, and one arrow otherwise.
    """
    strut_form.node_attributes(1, ["qx", "qy", "qz"], [1.0, -2.0, 0.0])
    node_xyz = strut_form.node_coordinates(1)

    split = form_drawing(strut_form, None, None, FormDisplaySettings())
    whole = form_drawing(strut_form, None, None, FormDisplaySettings(decompose=False))
    vectors = [subtract_vectors(load.end, load.start) for load in split.loads]

    assert vectors == [pytest.approx([1.0, 0.0, 0.0]), pytest.approx([0.0, -2.0, 0.0])]
    assert all(load.end == pytest.approx(node_xyz) for load in split.loads)
    assert len(whole.loads) == 1


def test_decompose_skips_small_components(strut_form):
    """
    Checks that a component smaller than force_min is not drawn.
    """
    strut_form.node_attributes(1, ["qx", "qy", "qz"], [0.0005, -2.0, 0.0])
    drawing = form_drawing(strut_form, None, None, FormDisplaySettings())

    assert len(drawing.loads) == 1


# ==============================================================================
# Thickening
# ==============================================================================


def test_settings_reject_few_thick_sides():
    """
    Checks that a thickened mesh needs at least three sides.
    """
    with pytest.raises(ValueError, match="at least 3 sides"):
        FormDisplaySettings(thick_sides=2)


def test_edges_trim_by_sphere_radius(chain_form):
    """
    Checks that every edge's thickened pipe stops one sphere radius short of
    its nodes, whatever its own radius, and that the forces carry no trim.
    """
    forces = {(0, 1): 1.0, (1, 2): 3.0, (2, 3): 2.0}
    for edge, force in forces.items():
        chain_form.edge_attribute(edge, "force", force)
    settings = FormDisplaySettings(radius_min=0.05, radius_max=0.2)

    drawing = form_drawing(chain_form, None, None, settings)
    arrows = drawing.loads + drawing.reactions

    assert [line.trim for line in drawing.edges] == [0.2, 0.2, 0.2]
    assert {arrow.trim for arrow in arrows} == {0.0}
