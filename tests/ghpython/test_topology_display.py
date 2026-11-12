from math import sqrt

import pytest

from compas.geometry import distance_point_point
from compas.geometry import midpoint_point_point

from compas_cem import COLORS
from compas_cem import LOAD_CROSS_SIZE
from compas_cem.ghpython import topology_drawing

# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def tower(braced_tower_2d):
    """
    A braced tower with its trails built, supported at 0 and 3, loaded at 2 and 5.
    """
    braced_tower_2d.build_trails()
    return braced_tower_2d


@pytest.fixture
def tree(tree_2d_needs_auxiliary_trails):
    """
    A tree with its auxiliary trails built.
    """
    tree_2d_needs_auxiliary_trails.build_trails(auxiliary_trails=True)
    return tree_2d_needs_auxiliary_trails


# ==============================================================================
# Nodes
# ==============================================================================


def test_nodes_colored_by_type(tower):
    """
    Checks that supports are green, origins purple and the rest white.
    """
    drawing = topology_drawing(tower, None, None, False)
    colors = [point.color for point in drawing.nodes]

    support = COLORS["node_support"]
    origin = COLORS["node_origin"]
    node = COLORS["node"]
    assert colors == [support, node, origin, support, node, origin]
    assert [point.color for point in drawing.origin_nodes] == [origin, origin]
    assert [point.color for point in drawing.support_nodes] == [support, support]


# ==============================================================================
# Edges
# ==============================================================================


def test_edges_colored_by_state(tower):
    """
    Checks that trail edges take the sign of their length and deviation edges
    the sign of their force.
    """
    drawing = topology_drawing(tower, None, [(0, 1), (1, 4), (1, 5)], False)
    colors = [line.color for line in drawing.edges]

    compression = COLORS["compression"]
    assert colors == [compression, compression, COLORS["tension"]]


def test_deviation_edges_are_dashed(tower):
    """
    Checks that every deviation edge is dashed and no trail edge is.
    """
    drawing = topology_drawing(tower, None, None, False)

    assert len(drawing.deviation_edges) == 5
    assert all(line.is_dashed for line in drawing.deviation_edges)
    assert not any(line.is_dashed for line in drawing.trail_edges)


def test_auxiliary_trails_are_orange(tree):
    """
    Checks that auxiliary trail edges and auxiliary trails are orange.
    """
    drawing = topology_drawing(tree, None, None, False)
    auxiliary = COLORS["auxiliary_trail"]
    trail_colors = [polyline.color for polyline in drawing.trails]

    assert sum(line.color == auxiliary for line in drawing.trail_edges) == 2
    assert trail_colors.count(auxiliary) == 2
    assert trail_colors.count(COLORS["trail"]) == 1


# ==============================================================================
# Loads
# ==============================================================================


def test_loaded_nodes_are_crossed(tower):
    """
    Checks that every loaded node gets two black lines crossing at it in the XY
    plane, each reaching the cross size of the diagonal from the node.
    """
    drawing = topology_drawing(tower, None, None, False)
    diagonal = sqrt(1.0**2 + 2.0**2)
    reach = LOAD_CROSS_SIZE * diagonal

    assert len(drawing.loads) == 4
    for line, node in zip(drawing.loads, [2, 2, 5, 5]):
        center = tower.node_coordinates(node)
        assert midpoint_point_point(line.start, line.end) == pytest.approx(center)
        assert distance_point_point(line.start, center) == pytest.approx(reach)
        assert line.start[2] == line.end[2] == center[2]
        assert line.color == COLORS["node_black"]


def test_node_selection_narrows_crosses(tower):
    """
    Checks that only the selected loaded nodes are crossed.
    """
    drawing = topology_drawing(tower, [0, 1, 2], None, False)

    assert len(drawing.nodes) == 3
    assert len(drawing.loads) == 2


# ==============================================================================
# Labels
# ==============================================================================


def test_labels_off_by_default(tower):
    """
    Checks that no label is drawn unless asked for.
    """
    drawing = topology_drawing(tower, None, None, False)

    assert drawing.labels == []


def test_labels_show_keys(tower):
    """
    Checks that the labels show the node keys and the edge keys as u-v.
    """
    drawing = topology_drawing(tower, [0, 1], [(0, 1)], True)
    texts = [label.text for label in drawing.labels]
    edge_point = midpoint_point_point(
        tower.node_coordinates(0), tower.node_coordinates(1)
    )

    assert texts == ["0", "1", "0-1"]
    assert drawing.labels[2].point == pytest.approx(edge_point)
