import pytest

# ==============================================================================
# Tests
# ==============================================================================

# TODO: A sanity check for nodes with no trails!

def test_trails_number(compression_strut):
    """
    Checks that the number of trails is correct.
    """
    form = compression_strut
    trails = form.trails()
    assert len(trails) == 1


def test_trails_first_last_node_types(compression_strut):
    """
    Test that the first node is root and the last a support.
    """
    form = compression_strut
    trails = form.trails()

    for root_key, trail in trails.items():

        assert form.is_node_root(trail[0])
        assert form.is_node_support(trail[-1])


def test_trails_type_intermediate_nodes(compression_strut):
    """
    Verify that all other nodes in a trail are neither root nor support.
    """
    form = compression_strut
    trails = form.trails()

    for root_key, trail in trails.items():
        trail.pop(0)
        trail.pop(-1)

        for node in trail:
            assert form.is_node_root(node) == False
            assert form.is_node_support(node) == False


def test_trails_nodes_unassigned(support_missing_form):
    """
    Fails because some nodes are unassigned after doing the trail search.
    """
    with pytest.raises(AssertionError):
        support_missing_form.trails()


def test_trails_no_trail_edges(no_trails_form):
    """
    Raises error because form contains only deviatione edges.
    """
    with pytest.raises(AssertionError):
        no_trails_form.trails()


def test_trails_no_supports(unsupported_form):
    """
    Trail search fails because form has no supports.
    """
    with pytest.raises(AssertionError):
        unsupported_form.trails()
