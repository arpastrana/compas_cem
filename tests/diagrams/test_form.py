import pytest

# ==============================================================================
# Tests
# ==============================================================================

@pytest.mark.parametrize("form,before,after", [(compression_strut, 0, 1)])
def test_root_nodes(form, before, after):
    """
    Verifies that the number of root nodes pre and post calling form.trails().
    """
    assert len(list(form.root_nodes())) == before
    form.trails()
    assert len(list(form.root_nodes())) == after
