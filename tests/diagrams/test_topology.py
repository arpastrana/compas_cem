import pytest
from compas.data import json_dumps
from compas.data import json_loads
from pytest_lazy_fixtures import lf

from compas_cem.diagrams import TopologyDiagram
from compas_cem.elements import Node
from compas_cem.elements import TrailEdge


# ==============================================================================
# Tests - Edges
# ==============================================================================


@pytest.mark.parametrize(
    "topology, edges",
    [
        (lf("compression_strut"), [(0, 1)]),
        (lf("threebar_funicular"), [(0, 1), (2, 3)]),
        (lf("braced_tower_2d"), [(0, 1), (1, 2), (3, 4), (4, 5)]),
    ],
)
def test_num_keys_trail_edges(topology, edges):
    """
    Checks that the returned trail edge keys are correct.
    """
    edges = set(edges)
    test_edges = set(topology.trail_edges(data=False))
    assert len(test_edges) == len(edges)
    assert edges == test_edges


@pytest.mark.parametrize(
    "topology, edges",
    [
        (lf("compression_strut"), []),
        (lf("threebar_funicular"), [(1, 2)]),
        (lf("braced_tower_2d"), [(1, 4), (2, 5), (1, 5), (1, 3), (2, 4)]),
    ],
)
def test_num_keys_deviation_edges(topology, edges):
    """
    Checks that the returned trail edge keys are correct.
    """
    edges = set(edges)
    test_edges = set(topology.deviation_edges(data=False))
    assert len(test_edges) == len(edges)
    assert edges == test_edges


# ==============================================================================
# Tests - Node Queries
# ==============================================================================


@pytest.mark.parametrize(
    "topology, num_origin",
    [(lf("compression_strut"), 1), (lf("threebar_funicular"), 2)],
)
def test_num_origin_nodes(topology, num_origin):
    """
    Verifies that the number of origin nodes pre and post calling topology.build_trails().
    """
    assert len(list(topology.origin_nodes())) == 0
    topology.build_trails()
    assert len(list(topology.origin_nodes())) == num_origin


@pytest.mark.parametrize(
    "topology, num_supports",
    [
        (lf("compression_strut"), 1),
        (lf("threebar_funicular"), 2),
        (lf("unsupported_topology"), 0),
    ],
)
def test_num_support_nodes(topology, num_supports):
    """
    Verifies that the number of support nodes is correct.
    """
    assert len(list(topology.support_nodes())) == num_supports


# ==============================================================================
# Tests - Connected Edges
# ==============================================================================


@pytest.mark.parametrize(
    "topology, node_key, num_edges",
    [
        (lf("compression_strut"), 0, 0),
        (lf("compression_strut"), 1, 0),
        (lf("threebar_funicular"), 0, 0),
        (lf("threebar_funicular"), 1, 1),
        (lf("threebar_funicular"), 2, 1),
        (lf("threebar_funicular"), 3, 0),
        (lf("braced_tower_2d"), 1, 3),
    ],
)
def test_num_connected_deviation_edges(topology, node_key, num_edges):
    """
    Checks that the number of deviation edges for a specific node is correct.
    """
    assert len(topology.connected_deviation_edges(node_key)) == num_edges


@pytest.mark.parametrize(
    "topology, node_key, edge_keys",
    [
        (lf("compression_strut"), 0, []),
        (lf("threebar_funicular"), 1, [(1, 2)]),
        (lf("threebar_funicular"), 2, [(1, 2)]),
        (lf("braced_tower_2d"), 5, [(1, 5), (2, 5)]),
    ],
)
def test_keys_connected_deviation_edges(topology, node_key, edge_keys):
    """
    Checks for the keys of the deviation edges connected to a node are correct.
    """
    assert set(topology.connected_deviation_edges(node_key)) == set(edge_keys)


@pytest.mark.parametrize(
    "topology, node_key, num_edges",
    [
        (lf("compression_strut"), 0, 1),
        (lf("compression_strut"), 1, 1),
        (lf("threebar_funicular"), 0, 1),
        (lf("threebar_funicular"), 1, 1),
        (lf("threebar_funicular"), 2, 1),
        (lf("threebar_funicular"), 3, 1),
        (lf("braced_tower_2d"), 4, 2),
        (lf("braced_tower_2d"), 2, 1),
    ],
)
def test_num_connected_trail_edges(topology, node_key, num_edges):
    """
    Checks that the number of trail edges for a specific node is correct.
    """
    assert len(topology.connected_trail_edges(node_key)) == num_edges


@pytest.mark.parametrize(
    "topology, node_key, edge_keys",
    [
        (lf("compression_strut"), 0, [(0, 1)]),
        (lf("threebar_funicular"), 1, [(0, 1)]),
        (lf("threebar_funicular"), 2, [(2, 3)]),
        (lf("braced_tower_2d"), 1, [(0, 1), (1, 2)]),
    ],
)
def test_keys_connected_trail_edges(topology, node_key, edge_keys):
    """
    Checks for the keys of the trail edges connected to a node are correct.
    Edge keys should remain the same as when edges were added.
    """
    assert set(topology.connected_trail_edges(node_key)) == set(edge_keys)


@pytest.mark.parametrize(
    "topology, node_key, edge_keys",
    [
        (lf("compression_strut"), 0, [(1, 2)]),
        (lf("braced_tower_2d"), 1, [(1, 0), (2, 2)]),
    ],
)
def test_fails_keys_connected_trail_edges(topology, node_key, edge_keys):
    """
    Checks for the keys of the trail edges connected to a node are incorrect.
    Edge keys should remain the same as when edges were added.
    """
    with pytest.raises(AssertionError):
        assert set(topology.connected_trail_edges(node_key)) == set(edge_keys)


@pytest.mark.parametrize(
    "topology, node_key, edge_keys",
    [
        (lf("compression_strut"), 0, []),
        (lf("braced_tower_2d"), 0, []),
        (lf("braced_tower_2d"), 1, [(1, 4)]),
        (lf("braced_tower_2d"), 2, [(2, 5)]),
        (lf("braced_tower_2d"), 5, [(2, 5)]),
        (lf("braced_tower_2d"), 4, [(1, 4)]),
    ],
)
def test_num_keys_direct_deviation_edges(topology, node_key, edge_keys):
    """
    Tests the number and the keys of direct deviation edges coming into a node.
    """
    topology.build_trails()
    test_edge_keys = topology._connected_direct_deviation_edges(node_key)
    assert len(test_edge_keys) == len(edge_keys)
    assert set(test_edge_keys) == set(edge_keys)


@pytest.mark.parametrize(
    "topology, node_key, edge_keys",
    [
        (lf("compression_strut"), 0, []),
        (lf("braced_tower_2d"), 0, []),
        (lf("braced_tower_2d"), 1, [(1, 3), (1, 5)]),
        (lf("braced_tower_2d"), 2, [(2, 4)]),
        (lf("braced_tower_2d"), 3, [(1, 3)]),
        (lf("braced_tower_2d"), 4, [(2, 4)]),
        (lf("braced_tower_2d"), 5, [(1, 5)]),
    ],
)
def test_num_keys_indirect_deviation_edges(topology, node_key, edge_keys):
    """
    Tests the number and the keys of indirect deviation edges coming into a node.
    """
    topology.build_trails()
    test_edge_keys = topology._connected_indirect_deviation_edges(node_key)
    assert len(test_edge_keys) == len(edge_keys)
    assert set(test_edge_keys) == set(edge_keys)


@pytest.mark.parametrize(
    "topology, node_key, num_deviation",
    [
        (lf("compression_strut"), 0, 0),
        (lf("braced_tower_2d"), 1, 3),
        (lf("braced_tower_2d"), 3, 1),
        (lf("braced_tower_2d"), 5, 2),
    ],
)
def test_num_direct_indirect_deviation_edges(topology, node_key, num_deviation):
    """
    Checks that the sum of direct and indirect deviation edges is correct.
    """
    topology.build_trails()
    indirect = topology._connected_indirect_deviation_edges(node_key)
    direct = topology._connected_direct_deviation_edges(node_key)
    assert len(indirect) + len(direct) == num_deviation


# ==============================================================================
# Polymorphic add_node and add_edge
# ==============================================================================


def test_add_node_accepts_an_element_and_a_key():
    """
    Checks that both node vocabularies reach the same diagram.
    """
    topology = TopologyDiagram()

    assert topology.add_node(Node(0, [1.0, 2.0, 3.0])) == 0
    assert topology.add_node(1, x=4.0, y=5.0, z=6.0) == 1
    assert topology.add_node(key=2, attr_dict={"x": 7.0}) == 2

    assert topology.number_of_nodes() == 3
    assert topology.node_coordinates(0) == [1.0, 2.0, 3.0]
    assert topology.node_coordinates(1) == [4.0, 5.0, 6.0]


def test_add_edge_accepts_an_element_and_two_keys():
    """
    Checks that both edge vocabularies reach the same diagram.
    """
    topology = TopologyDiagram()
    for key in range(4):
        topology.add_node(Node(key, [float(key), 0.0, 0.0]))

    assert topology.add_edge(TrailEdge(0, 1, length=-1.0)) == (0, 1)
    assert topology.add_edge(1, 2, attr_dict={"type": "deviation"}) == (1, 2)

    assert topology.number_of_edges() == 2
    assert topology.edge_length_2((0, 1)) == -1.0
    assert topology.edge_attribute((1, 2), "type") == "deviation"


def test_add_node_rejects_an_edge_element():
    """
    Checks that an edge element cannot slip through the node entry point.
    """
    topology = TopologyDiagram()
    with pytest.raises(TypeError):
        topology.add_node(TrailEdge(0, 1, length=-1.0))


def test_add_edge_rejects_a_node_element():
    """
    Checks that a node element cannot slip through the edge entry point.
    """
    topology = TopologyDiagram()
    with pytest.raises(TypeError):
        topology.add_edge(Node(0, [0.0, 0.0, 0.0]))


def test_add_node_rejects_a_duplicated_key():
    """
    Checks that a key cannot be given both positionally and by name.
    """
    topology = TopologyDiagram()
    with pytest.raises(ValueError):
        topology.add_node(0, key=1)


@pytest.mark.parametrize(
    "topology",
    [(lf("compression_strut")), (lf("threebar_funicular")), (lf("braced_tower_2d"))],
)
def test_diagram_survives_a_json_roundtrip(topology):
    """
    Checks that deserialization still reaches the base graph entry points.

    COMPAS 2 replays construction through `add_node` and `add_edge`, so a
    diagram that overrides them has to keep both vocabularies working.
    """
    other = json_loads(json_dumps(topology))

    assert other.number_of_nodes() == topology.number_of_nodes()
    assert other.number_of_edges() == topology.number_of_edges()

    for node in topology.nodes():
        assert other.node_coordinates(node) == topology.node_coordinates(node)

    for edge in topology.edges():
        assert other.edge_attribute(edge, "type") == topology.edge_attribute(
            edge, "type"
        )


@pytest.mark.parametrize(
    "topology",
    [(lf("compression_strut")), (lf("threebar_funicular")), (lf("braced_tower_2d"))],
)
def test_diagram_survives_a_copy(topology):
    """
    Checks that `copy()` works, which also replays through the entry points.
    """
    other = topology.copy()

    assert other.number_of_nodes() == topology.number_of_nodes()
    assert other.number_of_edges() == topology.number_of_edges()
