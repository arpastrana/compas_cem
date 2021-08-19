import pytest

import numpy as np

from compas.geometry import Plane

from compas_cem.equilibrium.force import trail_vector_out
from compas_cem.equilibrium.force import indirect_deviation_edges_resultant_vector
from compas_cem.equilibrium.force import direct_deviation_edges_resultant_vector
from compas_cem.equilibrium.force import deviation_edges_resultant_vector
from compas_cem.equilibrium.force import trail_edge_length_from_plane
from compas_cem.equilibrium.force import node_equilibrium

from compas_cem.equilibrium.force_numpy import trail_edge_length_from_plane_numpy

# ==============================================================================
# Tests - Equilibrium Helpers
# ==============================================================================

def test_trail_vector_out():
    """
    Tests that the output vector is correct.
    """
    for _ in range(10):
        vector_matrix = np.random.rand(4, 3)
        tvec_in, q_vec, rd_vec, ri_vec = vector_matrix.tolist()

        a = trail_vector_out(tvec_in, q_vec, rd_vec, ri_vec)
        b = -1.0 * np.sum(vector_matrix, axis=0)

        assert np.allclose(a, b)


def test_edge_length_from_plane():
    """
    Check that the trail length computed from a line-plane intersection is right.
    """
    pos = [1.0, 0.0, 0.0]
    direction = [0.0, 1.0, 0.0]
    plane_a = Plane([0.0, 2.0, 0.0], [0.0, 1.0, 0.0])
    plane_b = Plane([2.0, 0.0, 0.0], [1.0, 0.0, 0.0])

    length_a = trail_edge_length_from_plane(pos, direction, plane_a)
    length_b = trail_edge_length_from_plane(pos, direction, plane_b)

    assert np.allclose(length_a, 2.0), print(length_a)
    assert length_b is None  # no intersection


def test_edge_length_from_plane_numpy():
    """
    Check that the trail length computed from a line-plane intersection is right.
    But with numpy.
    """
    pos = np.array([1.0, 0.0, 0.0])
    direction = np.array([0.0, 1.0, 0.0])
    plane_a = (np.array([0.0, 2.0, 0.0]), np.array([0.0, 1.0, 0.0]))
    plane_b = (np.array([2.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0]))

    length_a = trail_edge_length_from_plane_numpy(pos, direction, plane_a)
    length_b = trail_edge_length_from_plane_numpy(pos, direction, plane_b)

    assert np.allclose(length_a, 2.0), print(length_a)
    assert length_b is None  # no intersection


@pytest.mark.parametrize("topology, node, resultant",
                         [(pytest.lazy_fixture("compression_strut"), 0, [0.0, 0.0, 0.0]),
                          (pytest.lazy_fixture("threebar_funicular"), 1, [-1.0, 0.0, 0.0]),
                          (pytest.lazy_fixture("threebar_funicular"), 2, [1.0, 0.0, 0.0]),
                          (pytest.lazy_fixture("braced_tower_2d"), 3, [-0.5*2**0.5, 0.5*2**0.5, 0.0])
                          ])
def test_deviation_edges_resultant_vector(topology, node, resultant):
    """
    Verifies that the output vector is correct.
    """
    node_xyz = {node: topology.node_coordinates(node) for node in topology.nodes()}
    edges = topology.connected_deviation_edges(node)
    a = deviation_edges_resultant_vector(topology, node, node_xyz, edges)
    b = resultant

    assert np.allclose(a, b)


@pytest.mark.parametrize("topology, node, resultant",
                         [(pytest.lazy_fixture("braced_tower_2d"), 1, [-1.0, 0.0, 0.0]),
                          (pytest.lazy_fixture("braced_tower_2d"), 5, [1.0, 0.0, 0.0])])
def test_direct_deviation_edges_resultant_vector(topology, node, resultant):
    """
    Verifies that the output vector is correct.
    """
    topology.build_trails()
    node_xyz = {node: topology.node_coordinates(node) for node in topology.nodes()}
    a = direct_deviation_edges_resultant_vector(topology, node, node_xyz)
    b = resultant

    assert np.allclose(a, b)


@pytest.mark.parametrize("topology, node, resultant",
                         [(pytest.lazy_fixture("braced_tower_2d"), 4, [-0.5*2**0.5, 0.5*2**0.5, 0.0]),
                          (pytest.lazy_fixture("braced_tower_2d"), 1, [2**0.5, 0.0, 0.0]),
                          (pytest.lazy_fixture("braced_tower_2d"), 0, [0.0, 0.0, 0.0])
                           ])
def test_indirect_deviation_edges_resultant_vector(topology, node, resultant):
    """
    Verifies that the output vector is correct.
    """
    topology.build_trails()
    node_xyz = {node: topology.node_coordinates(node) for node in topology.nodes()}
    a = indirect_deviation_edges_resultant_vector(topology, node, node_xyz)
    b = resultant

    assert np.allclose(a, b)


@pytest.mark.parametrize("topology, node, result",
                         [(pytest.lazy_fixture("compression_strut"), 1, [0.0, 1.0, 0.0]),
                          (pytest.lazy_fixture("threebar_funicular"), 2, [-1.0, 1.0, 0.0]),
                          (pytest.lazy_fixture("braced_tower_2d"), 5, [-1.0, 1.0, 0.0])
                           ])
def test_node_equilibrium_no_indirect_root_nodes(topology, node, result):
    """
    Checks that the resulting output vector is correct.
    """
    topology.build_trails()
    node_xyz = {node: topology.node_coordinates(node) for node in topology.nodes()}
    t_vec_in = [0.0, 0.0, 0.0]
    t_vec_out = node_equilibrium(topology, node, t_vec_in, node_xyz, indirect=False)

    assert np.allclose(t_vec_out, result)


@pytest.mark.parametrize("topology, node, result",
                         [(pytest.lazy_fixture("compression_strut"), 1, [0.0, 1.0, 0.0]),
                          (pytest.lazy_fixture("threebar_funicular"), 2, [-1.0, 1.0, 0.0]),
                          (pytest.lazy_fixture("braced_tower_2d"), 5,
                           [-1.0 * (1.0 - 0.5*2**0.5), -1 * (-1.0 - 0.5*2**0.5), 0.0])
                           ])
def test_node_equilibrium_with_indirect_root_nodes(topology, node, result):
    """
    Checks that the resulting output vector is correct.
    """
    topology.build_trails()
    node_xyz = {node: topology.node_coordinates(node) for node in topology.nodes()}
    t_vec_in = [0.0, 0.0, 0.0]
    t_vec_out = node_equilibrium(topology, node, t_vec_in, node_xyz, indirect=True)

    assert np.allclose(t_vec_out, result)
