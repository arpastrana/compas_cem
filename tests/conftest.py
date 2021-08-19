from math import sqrt

import pytest

from compas.geometry import Plane

from compas_cem.diagrams import TopologyDiagram
from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.elements import DeviationEdge
from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport

# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def compression_strut():
    """
    A one-edge, single-trail compression strut.
    """
    topology = TopologyDiagram()

    # add nodes
    topology.add_node(Node(0, [0.0, 0.0, 0.0]))
    topology.add_node(Node(1, [0.0, 2.0, 0.0]))
    # add edge with length 1, in compression
    topology.add_edge(TrailEdge(0, 1, length=-1.0))
    # add support
    topology.add_support(NodeSupport(0))
    # add loads at the unsupported edge
    topology.add_load(NodeLoad(1, [0, -1.0, 0.0]))

    return topology


@pytest.fixture
def tension_chain():
    """
    A chain with three edges in tension.
    The lengths of the first and the last edges are implicitly pulled to planes.
    """
    topology = TopologyDiagram()

    # add nodes
    topology.add_node(Node(0, [0.0, 0.0, 0.0]))
    topology.add_node(Node(1, [1.0, 0.0, 0.0]))
    topology.add_node(Node(2, [2.0, 0.0, 0.0]))
    topology.add_node(Node(3, [3.0, 0.0, 0.0]))
    # add edges
    topology.add_edge(TrailEdge(0, 1, length=1, plane=Plane([1.5, 0, 0], [1, 0, 0])))
    topology.add_edge(TrailEdge(1, 2, length=1))  # unit length in tension
    topology.add_edge(TrailEdge(2, 3, length=1, plane=Plane([4.0, 0, 0], [1, 0, 0])))
    # add support
    topology.add_support(NodeSupport(3))
    # add load
    topology.add_load(NodeLoad(0, [-1, 0, 0]))

    return topology


@pytest.fixture
def compression_chain():
    """
    A chain with three edges in compression.
    The lengths of the first and the last edges are implicitly pulled to planes.
    """
    topology = TopologyDiagram()

    # add nodes
    topology.add_node(Node(0, [0.0, 0.0, 0.0]))
    topology.add_node(Node(1, [1.0, 0.0, 0.0]))
    topology.add_node(Node(2, [2.0, 0.0, 0.0]))
    topology.add_node(Node(3, [3.0, 0.0, 0.0]))
    # add edges
    topology.add_edge(TrailEdge(0, 1, length=-1, plane=Plane([1.5, 0, 0], [1, 0, 0])))
    topology.add_edge(TrailEdge(1, 2, length=-1))  # unit length in tension
    topology.add_edge(TrailEdge(2, 3, length=-1, plane=Plane([4.0, 0, 0], [1, 0, 0])))
    # add support
    topology.add_support(NodeSupport(3))
    # add load
    topology.add_load(NodeLoad(0, [1, 0, 0]))

    return topology


@pytest.fixture
def threebar_funicular():
    """
    The simplest possible two-trail funicular structure in the CEM.
    """
    # create a topology diagram
    topology = TopologyDiagram()

    # add nodes
    topology.add_node(Node(0, [0.0, 0.0, 0.0]))
    topology.add_node(Node(1, [1.0, 0.0, 0.0]))
    topology.add_node(Node(2, [2.5, 0.0, 0.0]))
    topology.add_node(Node(3, [3.5, 0.0, 0.0]))

    # add edges with negative values for a compression-only structure
    topology.add_edge(TrailEdge(0, 1, length=-1.0))
    topology.add_edge(DeviationEdge(1, 2, force=-1.0))
    topology.add_edge(TrailEdge(2, 3, length=-1.0))

    # add supports
    topology.add_support(NodeSupport(0))
    topology.add_support(NodeSupport(3))

    # add loads
    topology.add_load(NodeLoad(1, [0.0, -1.0, 0.0]))
    topology.add_load(NodeLoad(2, [0.0, -1.0, 0.0]))

    return topology


@pytest.fixture
def braced_tower_2d():
    """
    A braced tower in 2d.
    """
    points = [(0, [0.0, 0.0, 0.0]),
              (1, [0.0, 1.0, 0.0]),
              (2, [0.0, 2.0, 0.0]),
              (3, [1.0, 0.0, 0.0]),
              (4, [1.0, 1.0, 0.0]),
              (5, [1.0, 2.0, 0.0])]

    trail_edges = [(0, 1),
                   (1, 2),
                   (3, 4),
                   (4, 5)]

    deviation_edges = [(1, 4),
                       (2, 5)]

    load = [0.0, -1.0, 0.0]

    topology = TopologyDiagram()

    for key, point in points:
        topology.add_node(Node(key, point))

    for u, v in trail_edges:
        topology.add_edge(TrailEdge(u, v, length=-1.0))

    for u, v in deviation_edges:
        topology.add_edge(DeviationEdge(u, v, force=-1.0))

    topology.add_edge(DeviationEdge(1, 5, force=1.0))
    topology.add_edge(DeviationEdge(1, 3, force=1.0))
    topology.add_edge(DeviationEdge(2, 4, force=1.0))

    topology.add_support(NodeSupport(0))
    topology.add_support(NodeSupport(3))

    topology.add_load(NodeLoad(2, load))
    topology.add_load(NodeLoad(5, load))

    return topology

@pytest.fixture
def tree_2d_needs_auxiliary_trails():
    """
    An planar tree that is missing two auxiliary trails to be valid topologically.
    """
    width = 4
    height = width / 2

    # Topology diagram
    topology = TopologyDiagram()

    # add nodes
    topology.add_node(Node(1, [-width / 2, height, 0.0]))
    topology.add_node(Node(2, [width / 2, height, 0.0]))
    topology.add_node(Node(3, [0.0, height / 2, 0.0]))
    topology.add_node(Node(4, [0.0, 0.0, 0.0]))

    # add edges with negative values for a compression-only structure
    topology.add_edge(TrailEdge(3, 4, length=-height/2))

    topology.add_edge(DeviationEdge(1, 3, force=-sqrt(4.0)))
    topology.add_edge(DeviationEdge(2, 3, force=-sqrt(2.0)))
    topology.add_edge(DeviationEdge(1, 2, force=2.0))

    # add supports
    topology.add_support(NodeSupport(4))

    # add loads
    topology.add_load(NodeLoad(1, [0.0, -1.0, 0.0]))
    topology.add_load(NodeLoad(2, [0.0, -1.0, 0.0]))

    return topology

@pytest.fixture
def support_missing_topology():
    """
    A topology with three edges supposed to topology two trails. One support is missing.
    """
    topology = TopologyDiagram()
    # add five nodes
    for node_key in range(5):
        topology.add_node(Node(node_key, xyz=[0.0, float(node_key), 0.0]))

    # add two trail edges and one weird deviation edge
    topology.add_edge(TrailEdge(0, 1, length=1))
    topology.add_edge(TrailEdge(1, 2, length=1))
    topology.add_edge(DeviationEdge(3, 4, force=1))

    # add load
    topology.add_load(NodeLoad(0, [0, -1.0, 0.0]))

    # add only one support
    topology.add_support(NodeSupport(2))

    return topology


@pytest.fixture
def no_trails_topology():
    """
    A topology with only two deviation edges.
    """
    topology = TopologyDiagram()
    # add five nodes
    for node_key in range(3):
        topology.add_node(Node(node_key, xyz=[0.0, float(node_key), 0.0]))

    # add two trail edges and one weird deviation edge
    topology.add_edge(DeviationEdge(0, 1, force=1))
    topology.add_edge(DeviationEdge(1, 2, force=1))

    # add load
    topology.add_load(NodeLoad(0, [0, -1.0, 0.0]))

    # add only one support
    topology.add_support(NodeSupport(2))

    return topology


@pytest.fixture
def unsupported_topology():
    """
    A topology with one trail edge and a node load, but no supports.
    """
    topology = TopologyDiagram()
    # add five nodes
    for node_key in range(2):
        topology.add_node(Node(node_key, xyz=[0.0, float(node_key), 0.0]))

    # add two trail edges and one weird deviation edge
    topology.add_edge(TrailEdge(0, 1, length=-1))

    # add load
    topology.add_load(NodeLoad(0, [0, -1.0, 0.0]))

    return topology
