import pytest

from compas_cem.diagrams import FormDiagram
from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.elements import DeviationEdge
from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport
from compas_cem.equilibrium import force_equilibrium

# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def compression_strut():
    """
    A one-edge, single-trail compression strut.
    """
    form = FormDiagram()

    # add nodes
    form.add_node(Node(0, [0.0, 0.0, 0.0]))
    form.add_node(Node(1, [0.0, 2.0, 0.0]))
    # add edge with length 1, in compression
    form.add_edge(TrailEdge(0, 1, length=-1.0))
    # add support
    form.add_support(NodeSupport(0))
    # add loads at the unsupported edge
    form.add_load(NodeLoad(1, [0, -1.0, 0.0]))

    return form


@pytest.fixture
def threebar_funicular():
    """
    The simplest possible two-trail funicular structure in the CEM.
    """
    # create a form diagram
    form = FormDiagram()

    # add nodes
    form.add_node(Node(0, [0.0, 0.0, 0.0]))
    form.add_node(Node(1, [1.0, 0.0, 0.0]))
    form.add_node(Node(2, [2.0, 0.0, 0.0]))
    form.add_node(Node(3, [3.0, 0.0, 0.0]))

    # add edges with negative values for a compression-only structure
    form.add_edge(TrailEdge(0, 1, length=-1.0))
    form.add_edge(DeviationEdge(1, 2, force=-1.0))
    form.add_edge(TrailEdge(2, 3, length=-1.0))

    # add supports
    form.add_support(NodeSupport(0))
    form.add_support(NodeSupport(3))

    # add loads
    form.add_load(NodeLoad(1, [0.0, -1.0, 0.0]))
    form.add_load(NodeLoad(2, [0.0, -1.0, 0.0]))

    return form


@pytest.fixture
def support_missing_form():
    """
    A form with three edges supposed to form two trails. One support is missing.
    """
    form = FormDiagram()
    # add five nodes
    for node_key in range(5):
        form.add_node(Node(node_key, xyz=[0.0, float(node_key), 0.0]))

    # add two trail edges and one weird deviation edge
    form.add_edge(TrailEdge(0, 1, length=1))
    form.add_edge(TrailEdge(1, 2, length=1))
    form.add_edge(DeviationEdge(3, 4, force=1))

    # add load
    form.add_load(NodeLoad(0, [0, -1.0, 0.0]))

    # add only one support
    form.add_support(NodeSupport(2))

    return form


@pytest.fixture
def no_trails_form():
    """
    A form with only two deviation edges.
    """
    form = FormDiagram()
    # add five nodes
    for node_key in range(3):
        form.add_node(Node(node_key, xyz=[0.0, float(node_key), 0.0]))

    # add two trail edges and one weird deviation edge
    form.add_edge(DeviationEdge(0, 1, force=1))
    form.add_edge(DeviationEdge(1, 2, force=1))

    # add load
    form.add_load(NodeLoad(0, [0, -1.0, 0.0]))

    # add only one support
    form.add_support(NodeSupport(2))

    return form


@pytest.fixture
def unsupported_form():
    """
    A form with one trail edge and a node load, but no supports.
    """
    form = FormDiagram()
    # add five nodes
    for node_key in range(2):
        form.add_node(Node(node_key, xyz=[0.0, float(node_key), 0.0]))

    # add two trail edges and one weird deviation edge
    form.add_edge(TrailEdge(0, 1, length=-1))

    # add load
    form.add_load(NodeLoad(0, [0, -1.0, 0.0]))

    return form
