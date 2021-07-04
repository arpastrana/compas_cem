import pytest

# ==============================================================================
# Tests
# ==============================================================================

# TODO: A sanity check for nodes with no trails!

def test_trails_number(compression_strut):
    """
    Checks that the number of trails is correct.
    """
    topology = compression_strut
    trails = topology.build_trails()
    assert len(trails) == 1


def test_trails_first_last_node_types(compression_strut):
    """
    Test that the first node is origin and the last a support.
    """
    topology = compression_strut
    trails = topology.build_trails()

    for origin_key, trail in trails.items():

        assert topology.is_node_origin(trail[0])
        assert topology.is_node_support(trail[-1])


def test_trails_type_intermediate_nodes(compression_strut):
    """
    Verify that all other nodes in a trail are neither origin nor support.
    """
    topology = compression_strut
    trails = topology.build_trails()

    for origin_key, trail in trails.items():
        trail.pop(0)
        trail.pop(-1)

        for node in trail:
            assert topology.is_node_origin(node) == False
            assert topology.is_node_support(node) == False


def test_trails_nodes_unassigned(support_missing_topology):
    """
    Fails because some nodes are unassigned after doing the trail search.
    """
    with pytest.raises(AssertionError):
        support_missing_topology.build_trails()


def test_trails_no_trail_edges(no_trails_topology):
    """
    Raises error because topology contains only deviatione edges.
    """
    with pytest.raises(AssertionError):
        no_trails_topology.build_trails()


def test_trails_no_supports(unsupported_topology):
    """
    Trail search fails because topology has no supports.
    """
    with pytest.raises(AssertionError):
        unsupported_topology.build_trails()
