import pytest


# ==============================================================================
# Tests
# ==============================================================================

@pytest.mark.parametrize("form, num_root",
                         [(pytest.lazy_fixture("compression_strut"), 1),
                          (pytest.lazy_fixture("threebar_funicular"), 2)
                          ])
def test_num_root_nodes(form, num_root):
    """
    Verifies that the number of root nodes pre and post calling form.trails().
    """
    assert len(list(form.root_nodes())) == 0
    form.trails()
    assert len(list(form.root_nodes())) == num_root


@pytest.mark.parametrize("form, num_supports",
                         [(pytest.lazy_fixture("compression_strut"), 1),
                          (pytest.lazy_fixture("threebar_funicular"), 2),
                          (pytest.lazy_fixture("unsupported_form"), 0)
                          ])
def test_num_support_nodes(form, num_supports):
    """
    Verifies that the number of support nodes is correct.
    """
    assert len(list(form.support_nodes())) == num_supports
