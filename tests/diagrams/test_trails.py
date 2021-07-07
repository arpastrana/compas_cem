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
    topology.build_trails()
    assert len(topology.trails()) == 1


def test_trails_first_last_node_types(compression_strut):
    """
    Test that the first node is origin and the last a support.
    """
    topology = compression_strut
    topology.build_trails()

    for trail in topology.trails():

        assert topology.is_node_origin(trail[0]) == True
        assert topology.is_node_support(trail[-1]) == True


def test_trails_type_intermediate_nodes(compression_strut):
    """
    Verify that all other nodes in a trail are neither origin nor support.
    """
    topology = compression_strut
    topology.build_trails()

    for trail in topology.trails():
        trail = list(trail)
        trail.pop(0)
        trail.pop(-1)

        for node in trail:
            assert topology.is_node_origin(node) == False
            assert topology.is_node_support(node) == False


@pytest.mark.parametrize("topology",
                         [(pytest.lazy_fixture("support_missing_topology")),
                          (pytest.lazy_fixture("tree_2d_needs_auxiliary_trails"))])
def test_trails_nodes_unassigned(topology):
    """
    Fails because some nodes are unassigned after doing the trail search.
    """
    with pytest.raises(AssertionError):
        topology.build_trails()


def test_trails_no_trail_edges(no_trails_topology):
    """
    Raises error because topology contains only deviation edges.
    """
    with pytest.raises(AssertionError):
        no_trails_topology.build_trails()


def test_trails_no_supports(unsupported_topology):
    """
    Trail search fails because topology has no supports.
    """
    with pytest.raises(AssertionError):
        unsupported_topology.build_trails()


@pytest.mark.parametrize("topology",
                         [(pytest.lazy_fixture("tree_2d_needs_auxiliary_trails"))])
def test_auxiliary_trails_auto(topology):
    """
    Appends auxiliary trails at the nodes shared one or more deviation edges.
    """
    trails_set = set([(3, 4), (1, 5), (2, 6)])
    aux_trails_set = set([(1, 5), (2, 6)])
    topology.build_trails(auxiliary_trails=True)

    assert topology.number_of_trails() == 3
    assert topology.number_of_auxiliary_trails() == 2
    assert trails_set == set(topology.trails())
    assert aux_trails_set == set(topology.auxiliary_trails())
    assert aux_trails_set == set(topology.auxiliary_trail_edges())
    assert set(topology.trails()) - set(topology.auxiliary_trails()) == {(3, 4)}

@pytest.mark.parametrize("topology",
                         [(pytest.lazy_fixture("compression_strut")),
                          (pytest.lazy_fixture("threebar_funicular")),
                          (pytest.lazy_fixture("braced_tower_2d"))])
def test_auxiliary_trails_empty(topology):
    """
    Checks that neither auxiliary trails nor auxiliary edges exist in the diagram.
    """
    topology.build_trails(auxiliary_trails=False)

    assert topology.number_of_auxiliary_trails() == 0
    assert len(list(topology.auxiliary_trails())) == 0
    assert len(list(topology.auxiliary_trail_edges())) == 0
