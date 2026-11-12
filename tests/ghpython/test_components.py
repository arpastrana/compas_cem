from pathlib import Path

import compas_cem

COMPONENTS_FOLDER = (
    Path(__file__).parents[2] / "src" / "compas_cem" / "ghpython" / "components_cpython"
)

# ==============================================================================
# Tests
# ==============================================================================


def test_component_headers():
    """
    Checks that every component requires the current version, which the release bump rewrites.
    """
    header = f"# r: compas_cem>={compas_cem.__version__}"
    scripts = sorted(COMPONENTS_FOLDER.glob("*/code.py"))
    first_lines = {
        script.parent.name: script.read_text(encoding="utf-8").splitlines()[0]
        for script in scripts
    }
    stale = [name for name, line in first_lines.items() if line != header]

    assert len(scripts) > 0
    assert stale == []
