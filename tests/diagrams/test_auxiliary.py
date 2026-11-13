import pytest
from compas.data import json_dumps
from compas.data import json_loads

from compas_cem.diagrams import TopologyDiagram

# ==============================================================================
# Tests
# ==============================================================================


def test_auxiliary_support_nodes(tree_2d_needs_auxiliary_trails):
    """
    Checks that the auxiliary support nodes are the supports the auxiliary trails added.
    """
    topology = tree_2d_needs_auxiliary_trails
    supports_before = set(topology.support_nodes())
    topology.build_trails(auxiliary_trails=True)
    supports_added = set(topology.support_nodes()) - supports_before

    assert set(topology.auxiliary_support_nodes()) == supports_added
    assert len(supports_added) == 2


def test_auxiliary_support_nodes_without_auxiliary_trails(compression_strut):
    """
    Checks that a topology without auxiliary trails has no auxiliary support nodes.
    """
    topology = compression_strut
    topology.build_trails()

    assert list(topology.auxiliary_support_nodes()) == []


def test_auxiliary_support_nodes_survive_data(tree_2d_needs_auxiliary_trails):
    """
    Checks that the auxiliary support nodes are found after a JSON round trip.
    """
    topology = tree_2d_needs_auxiliary_trails
    topology.build_trails(auxiliary_trails=True)
    text = json_dumps(topology)
    loaded = json_loads(text)

    assert isinstance(loaded, TopologyDiagram)
    assert set(loaded.auxiliary_support_nodes()) == set(
        topology.auxiliary_support_nodes()
    )


@pytest.mark.parametrize("length", [2.0, -2.0])
def test_auxiliary_supports_follow_vector(tree_2d_needs_auxiliary_trails, length):
    """
    Checks that an auxiliary support lies along the vector whatever the sign of
    the length, and that its edge keeps the signed length.
    """
    topology = tree_2d_needs_auxiliary_trails
    topology.auxiliary_trail_length = length
    topology.auxiliary_trail_vector = [0.0, -3.0, 0.0]
    topology.build_trails(auxiliary_trails=True)

    for node, edge in topology.auxiliary_trails(keys=True):
        u, v = edge
        support = v if u == node else u
        node_xyz = topology.node_coordinates(node)
        support_xyz = topology.node_coordinates(support)
        expected_xyz = [node_xyz[0], node_xyz[1] - 2.0, node_xyz[2]]

        assert support_xyz == pytest.approx(expected_xyz)
        assert topology.edge_attribute(edge, "length") == length
