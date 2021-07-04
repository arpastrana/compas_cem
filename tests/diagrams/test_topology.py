import pytest


# ==============================================================================
# Tests - Edges
# ==============================================================================

@pytest.mark.parametrize("topology, edges",
                         [(pytest.lazy_fixture("compression_strut"), [(0, 1)]),
                          (pytest.lazy_fixture("threebar_funicular"), [(0, 1), (2, 3)]),
                          (pytest.lazy_fixture("braced_tower_2d"), [(0, 1), (1, 2), (3, 4), (4, 5)])])
def test_num_keys_trail_edges(topology, edges):
    """
    Checks that the returned trail edge keys are correct.
    """
    edges = set(edges)
    test_edges = set(topology.trail_edges(data=False))
    assert len(test_edges) == len(edges)
    assert edges == test_edges


@pytest.mark.parametrize("topology, edges",
                         [(pytest.lazy_fixture("compression_strut"), []),
                          (pytest.lazy_fixture("threebar_funicular"), [(1, 2)]),
                          (pytest.lazy_fixture("braced_tower_2d"), [(1, 4), (2, 5), (1, 5), (1, 3), (2, 4)])])
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

@pytest.mark.parametrize("topology, num_origin",
                         [(pytest.lazy_fixture("compression_strut"), 1),
                          (pytest.lazy_fixture("threebar_funicular"), 2)])
def test_num_origin_nodes(topology, num_origin):
    """
    Verifies that the number of origin nodes pre and post calling topology.build_trails().
    """
    assert len(list(topology.origin_nodes())) == 0
    topology.build_trails()
    assert len(list(topology.origin_nodes())) == num_origin


@pytest.mark.parametrize("topology, num_supports",
                         [(pytest.lazy_fixture("compression_strut"), 1),
                          (pytest.lazy_fixture("threebar_funicular"), 2),
                          (pytest.lazy_fixture("unsupported_topology"), 0)])
def test_num_support_nodes(topology, num_supports):
    """
    Verifies that the number of support nodes is correct.
    """
    assert len(list(topology.support_nodes())) == num_supports


# ==============================================================================
# Tests - Connected Edges
# ==============================================================================

@pytest.mark.parametrize("topology, node_key, num_edges",
                         [(pytest.lazy_fixture("compression_strut"), 0, 0),
                          (pytest.lazy_fixture("compression_strut"), 1, 0),
                          (pytest.lazy_fixture("threebar_funicular"), 0, 0),
                          (pytest.lazy_fixture("threebar_funicular"), 1, 1),
                          (pytest.lazy_fixture("threebar_funicular"), 2, 1),
                          (pytest.lazy_fixture("threebar_funicular"), 3, 0),
                          (pytest.lazy_fixture("braced_tower_2d"), 1, 3)])
def test_num_connected_deviation_edges(topology, node_key, num_edges):
    """
    Checks that the number of deviation edges for a specific node is correct.
    """
    assert len(topology.connected_deviation_edges(node_key)) == num_edges


@pytest.mark.parametrize("topology, node_key, edge_keys",
                          [(pytest.lazy_fixture("compression_strut"), 0, []),
                           (pytest.lazy_fixture("threebar_funicular"), 1, [(1, 2)]),
                           (pytest.lazy_fixture("threebar_funicular"), 2, [(1, 2)]),
                           (pytest.lazy_fixture("braced_tower_2d"), 5, [(1, 5), (2, 5)])])
def test_keys_connected_deviation_edges(topology, node_key, edge_keys):
    """
    Checks for the keys of the deviation edges connected to a node are correct.
    """
    assert set(topology.connected_deviation_edges(node_key)) == set(edge_keys)


@pytest.mark.parametrize("topology, node_key, num_edges",
                         [(pytest.lazy_fixture("compression_strut"), 0, 1),
                          (pytest.lazy_fixture("compression_strut"), 1, 1),
                          (pytest.lazy_fixture("threebar_funicular"), 0, 1),
                          (pytest.lazy_fixture("threebar_funicular"), 1, 1),
                          (pytest.lazy_fixture("threebar_funicular"), 2, 1),
                          (pytest.lazy_fixture("threebar_funicular"), 3, 1),
                          (pytest.lazy_fixture("braced_tower_2d"), 4, 2),
                          (pytest.lazy_fixture("braced_tower_2d"), 2, 1)])
def test_num_connected_trail_edges(topology, node_key, num_edges):
    """
    Checks that the number of trail edges for a specific node is correct.
    """
    assert len(topology.connected_trail_edges(node_key)) == num_edges


@pytest.mark.parametrize("topology, node_key, edge_keys",
                          [(pytest.lazy_fixture("compression_strut"), 0, [(0, 1)]),
                           (pytest.lazy_fixture("threebar_funicular"), 1, [(0, 1)]),
                           (pytest.lazy_fixture("threebar_funicular"), 2, [(2, 3)]),
                           (pytest.lazy_fixture("braced_tower_2d"), 1, [(0, 1), (1, 2)])])
def test_keys_connected_trail_edges(topology, node_key, edge_keys):
    """
    Checks for the keys of the trail edges connected to a node are correct.
    Edge keys should remain the same as when edges were added.
    """
    assert set(topology.connected_trail_edges(node_key)) == set(edge_keys)


@pytest.mark.parametrize("topology, node_key, edge_keys",
                          [(pytest.lazy_fixture("compression_strut"), 0, [(1, 2)]),
                           (pytest.lazy_fixture("braced_tower_2d"), 1, [(1, 0), (2, 2)])])
def test_fails_keys_connected_trail_edges(topology, node_key, edge_keys):
    """
    Checks for the keys of the trail edges connected to a node are incorrect.
    Edge keys should remain the same as when edges were added.
    """
    with pytest.raises(AssertionError):
        assert set(topology.connected_trail_edges(node_key)) == set(edge_keys)


@pytest.mark.parametrize("topology, node_key, edge_keys",
                          [(pytest.lazy_fixture("compression_strut"), 0, []),
                           (pytest.lazy_fixture("braced_tower_2d"), 0, []),
                           (pytest.lazy_fixture("braced_tower_2d"), 1, [(1, 4)]),
                           (pytest.lazy_fixture("braced_tower_2d"), 2, [(2, 5)]),
                           (pytest.lazy_fixture("braced_tower_2d"), 5, [(2, 5)]),
                           (pytest.lazy_fixture("braced_tower_2d"), 4, [(1, 4)])])
def test_num_keys_direct_deviation_edges(topology, node_key, edge_keys):
    """
    Tests the number and the keys of direct deviation edges coming into a node.
    """
    topology.build_trails()
    test_edge_keys = topology._connected_direct_deviation_edges(node_key)
    assert len(test_edge_keys) == len(edge_keys)
    assert set(test_edge_keys) == set(edge_keys)


@pytest.mark.parametrize("topology, node_key, edge_keys",
                          [(pytest.lazy_fixture("compression_strut"), 0, []),
                           (pytest.lazy_fixture("braced_tower_2d"), 0, []),
                           (pytest.lazy_fixture("braced_tower_2d"), 1, [(1, 3), (1, 5)]),
                           (pytest.lazy_fixture("braced_tower_2d"), 2, [(2, 4)]),
                           (pytest.lazy_fixture("braced_tower_2d"), 3, [(1, 3)]),
                           (pytest.lazy_fixture("braced_tower_2d"), 4, [(2, 4)]),
                           (pytest.lazy_fixture("braced_tower_2d"), 5, [(1, 5)])])
def test_num_keys_indirect_deviation_edges(topology, node_key, edge_keys):
    """
    Tests the number and the keys of indirect deviation edges coming into a node.
    """
    topology.build_trails()
    test_edge_keys = topology._connected_indirect_deviation_edges(node_key)
    assert len(test_edge_keys) == len(edge_keys)
    assert set(test_edge_keys) == set(edge_keys)


@pytest.mark.parametrize("topology, node_key, num_deviation",
                          [(pytest.lazy_fixture("compression_strut"), 0, 0),
                           (pytest.lazy_fixture("braced_tower_2d"), 1, 3),
                           (pytest.lazy_fixture("braced_tower_2d"), 3, 1),
                           (pytest.lazy_fixture("braced_tower_2d"), 5, 2)])
def test_num_direct_indirect_deviation_edges(topology, node_key, num_deviation):
    """
    Checks that the sum of direct and indirect deviation edges is correct.
    """
    topology.build_trails()
    indirect = topology._connected_indirect_deviation_edges(node_key)
    direct = topology._connected_direct_deviation_edges(node_key)
    assert len(indirect) + len(direct) == num_deviation
