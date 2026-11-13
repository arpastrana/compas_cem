import pytest

from compas_cem.diagrams import TopologyDiagram
from compas_cem.elements import DeviationEdge
from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.equilibrium import static_equilibrium
from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport

# ==============================================================================
# Fixtures
# ==============================================================================


def two_trails(deviation_edges, is_unequal):
    """
    Two vertical trails supported at their bottom nodes and loaded at their top
    nodes, the right one a node longer if unequal, tied by deviation edges.
    """
    topology = TopologyDiagram()
    left_nodes = [0, 1, 2, 3]
    right_nodes = [4, 5, 6, 7, 8] if is_unequal else [4, 5, 6, 7]

    load_vector = [0.0, -1.0, 0.0]
    trail_columns = [(left_nodes, 0.0), (right_nodes, 1.0)]

    for nodes, x in trail_columns:
        for height, node in enumerate(reversed(nodes)):
            xyz = [x, float(height), 0.0]
            node_element = Node(node, xyz)
            topology.add_node(node_element)
        for u, v in zip(nodes[:-1], nodes[1:]):
            trail_edge = TrailEdge(u, v, length=-1.0)
            topology.add_edge(trail_edge)
        support = NodeSupport(nodes[-1])
        load = NodeLoad(nodes[0], load_vector)
        topology.add_support(support)
        topology.add_load(load)

    for u, v in deviation_edges:
        deviation_edge = DeviationEdge(u, v, force=-1.0)
        topology.add_edge(deviation_edge)

    topology.build_trails()

    return topology


@pytest.fixture
def interior_ladder():
    """
    Two trails of unequal length tied only at interior nodes, all at one height.
    """
    ties = [(1, 6), (2, 7)]
    topology = two_trails(ties, True)

    return topology


@pytest.fixture
def brace_first_ladder():
    """
    Two equal trails tied by a diagonal brace, added first, and two level ties.
    """
    brace_and_ties = [(1, 6), (1, 5), (2, 6)]
    topology = two_trails(brace_and_ties, False)

    return topology


# ==============================================================================
# Tests
# ==============================================================================


def test_align_makes_ties_direct(interior_ladder):
    """
    Checks that trails tied at interior nodes line up, the longer one first.
    """
    assert interior_ladder.number_of_indirect_deviation_edges() == 2

    interior_ladder.align_trails()

    assert interior_ladder.number_of_indirect_deviation_edges() == 0
    assert interior_ladder.node_sequence(4) == 0
    assert interior_ladder.node_sequence(0) == 1


def test_align_solves_in_one_iteration(interior_ladder):
    """
    Checks that an aligned topology needs a single solver iteration.
    """
    interior_ladder.align_trails()
    form_once = static_equilibrium(interior_ladder, tmax=1)
    form_converged = static_equilibrium(interior_ladder, tmax=100)

    for node in form_once.nodes():
        xyz_once = form_once.node_coordinates(node)
        xyz_converged = form_converged.node_coordinates(node)
        assert xyz_once == pytest.approx(xyz_converged)


def test_align_follows_most_edges(brace_first_ladder):
    """
    Checks that the gap most edges agree on wins over the edge added first.
    """
    brace_first_ladder.align_trails()

    assert brace_first_ladder.number_of_indirect_deviation_edges() == 1
    assert brace_first_ladder.is_indirect_deviation_edge((1, 6))
    assert brace_first_ladder.number_of_sequences() == 4


def test_align_keeps_braces_compact(braced_tower_2d):
    """
    Checks that braces no shift can make direct leave the sequences as built.
    """
    braced_tower_2d.build_trails()
    indirect_before = braced_tower_2d.number_of_indirect_deviation_edges()

    braced_tower_2d.align_trails()

    assert braced_tower_2d.number_of_indirect_deviation_edges() == indirect_before
    assert braced_tower_2d.number_of_sequences() == 3


def test_align_discards_earlier_shifts(interior_ladder):
    """
    Checks that every group of linked trails starts at sequence 0 again.
    """
    interior_ladder.shift_trail(0, 5)
    interior_ladder.shift_trail(4, 3)

    interior_ladder.align_trails()

    assert interior_ladder.node_sequence(4) == 0
    assert interior_ladder.number_of_indirect_deviation_edges() == 0


def test_align_needs_trails():
    """
    Checks that aligning a topology without trails raises.
    """
    topology = TopologyDiagram()

    with pytest.raises(ValueError, match="no trails"):
        topology.align_trails()
