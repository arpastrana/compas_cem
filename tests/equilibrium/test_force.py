from math import sqrt

import pytest

import numpy as np

from compas_cem.equilibrium import static_equilibrium
from compas_cem.equilibrium.force_numpy import static_equilibrium_numpy

from compas_cem.equilibrium.force import trail_vector_out
from compas_cem.equilibrium.force import indirect_deviation_edges_resultant_vector
from compas_cem.equilibrium.force import direct_deviation_edges_resultant_vector
from compas_cem.equilibrium.force import deviation_edges_resultant_vector
from compas_cem.equilibrium.force import node_equilibrium

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


# ==============================================================================
# Tests - Force Equilibrium
# ==============================================================================

def cs_out():
    output = {}
    output["xyz"] = {0: [0.0, 1.0, 0.0], 1: [0.0, 2.0, 0.0]}
    output["force"] = {(0, 1): -1.0}
    output["length"] = {(0, 1): 1.0}
    output["residual"] = {0: [0.0, 1.0, 0.0]}

    return output


def tf_out():
    output = {}
    output["xyz"] = {0: [0.29289321881345254, -0.7071067811865475, 0.0],
                     1: [1.0, 0.0, 0.0],
                     2: [2.5, 0.0, 0.0],
                     3: [3.207106, -0.7071067, 0.0]}

    output["force"] = {(0, 1): -1.414213561,
                       (1, 2): -1.0,
                       (2, 3): -1.41421356}

    output["length"] = {(0, 1): 1.0,
                        (1, 2): 1.5,
                        (2, 3): 1.0}

    output["residual"] = {0: [1.0, 1.0, -0.0],
                          3: [-1.0, 1.0, 0.0]}

    return output



def bt2_out():
    output = {}
    output["xyz"] = {0: [0.11891271935545733, 0.04623304043571308, 0.0],
                     1: [-0.14550216351451895, 1.0106420665842952, 0.0],
                     2: [0.0, 2.0, 0.0],
                     3: [1.5829003695589805, 0.11137412111377487, 0.0],
                     4: [1.1455022100524879, 1.010642073428508, 0.0],
                     5: [1.0, 2.0, 0.0]}

    output["force"] = {(0, 1): -1.5154917766302523,
                       (1, 2): -1.6714301665432025,
                       (1, 4): -1.0,
                       (1, 5): 1.0,
                       (1, 3): 1.0,
                       (2, 5): -1.0,
                       (2, 4): 1.0,
                       (3, 4): -1.1120156232900127,
                       (4, 5): -1.6714302901903129}

    output["length"] = {(0, 1): 1.0,
                        (1, 2): 1.0,
                        (1, 4): 1.2910043735670067,
                        (1, 5): 1.5136063976572767,
                        (1, 3): 1.9483475444811331,
                        (2, 5): 1.0,
                        (2, 4): 1.5136064284036903,
                        (3, 4): 1.0,
                        (4, 5): 1.0}

    output["residual"] = {0: [-0.4007185806081004, 1.4615539484361662, -0.0],
                          3: [-0.48639358696951673, 1.0000000124980013, -0.0]}

    return output


@pytest.mark.parametrize("topology, output",
                         [(pytest.lazy_fixture("compression_strut"), cs_out()),
                          (pytest.lazy_fixture("threebar_funicular"), tf_out()),
                          (pytest.lazy_fixture("braced_tower_2d"), bt2_out())
                          ])
def test_force_equilibrium_output(topology, output):
    """
    Minute testing of forces and geometric outputs post force equilibrium.
    """
    node_xyz_out = output["xyz"]
    edge_force_out = output["force"]
    edge_length_out = output["length"]
    support_residual_out = output["residual"]

    topology.build_trails()
    form = static_equilibrium(topology, eta=1e-5, tmax=100, verbose=False)

    check_nodes_xyz(form, node_xyz_out)
    check_edges_forces(form, edge_force_out)
    check_edges_lengths(form, edge_length_out)
    check_nodes_reactions(form, support_residual_out)


@pytest.mark.parametrize("topology, output",
                         [(pytest.lazy_fixture("compression_strut"), cs_out()),
                          (pytest.lazy_fixture("threebar_funicular"), tf_out()),
                          (pytest.lazy_fixture("braced_tower_2d"), bt2_out())
                          ])
def test_force_equilibrium_numpy_output(topology, output):
    """
    Minute testing of forces and geometric outputs post force equilibrium.
    """
    node_xyz_out = output["xyz"]
    edge_force_out = output["force"]
    edge_length_out = output["length"]
    support_residual_out = output["residual"]

    topology.build_trails()
    form = static_equilibrium_numpy(topology, eta=1e-5, tmax=100, verbose=False)

    check_nodes_xyz(form, node_xyz_out)
    check_edges_forces(form, edge_force_out)
    check_edges_lengths(form, edge_length_out)
    check_nodes_reactions(form, support_residual_out)

# ==============================================================================
# Tests - Force Equilibrium Helpers
# ==============================================================================

def check_nodes_xyz(form, node_xyz_out):
    for node in form.nodes(data=False):
        xyz = node_xyz_out.get(node)
        test_xyz = form.node_coordinates(node)
        assert np.allclose(xyz, test_xyz)


def check_edges_forces(form, edge_force_out):
    for edge in form.edges(data=False):
        force = edge_force_out.get(edge)
        test_force = form.edge_force(edge)
        assert np.allclose(force, test_force)


def check_edges_lengths(form, edge_length_out):
    for edge in form.edges(data=False):
        length = edge_length_out.get(edge)
        test_length = form.edge_length(*edge)  # TODO: overwrite inheritance
        assert np.allclose(length, test_length)


def check_nodes_reactions(form, support_residual_out):
    for node in form.nodes(data=False):
        residual = support_residual_out.get(node, [0.0, 0.0, 0.0])
        test_residual = form.reaction_force(node)
        assert np.allclose(residual, test_residual)
