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
