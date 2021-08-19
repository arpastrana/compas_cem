from math import sqrt

import pytest

import numpy as np

from compas_cem.equilibrium import static_equilibrium
from compas_cem.equilibrium.force_numpy import static_equilibrium_numpy


# ==============================================================================
# Tests - Force Equilibrium
# ==============================================================================


def cs_out():
    """Static equilibrium results from compression strut."""
    output = {}
    output["xyz"] = {0: [0.0, 1.0, 0.0], 1: [0.0, 2.0, 0.0]}
    output["force"] = {(0, 1): -1.0}
    output["length"] = {(0, 1): 1.0}
    output["residual"] = {0: [0.0, 1.0, 0.0]}

    return output


def tc_out():
    """Static equilibrium results from tension chain."""
    output = {}
    output["xyz"] = {0: [0.0, 0.0, 0.0],
                     1: [1.5, 0.0, 0.0],
                     2: [2.5, 0.0, 0.0],
                     3: [4.0, 0.0, 0.0]}

    output["force"] = {(0, 1): 1.0,
                       (1, 2): 1.0,
                       (2, 3): 1.0}

    output["length"] = {(0, 1): 1.5,
                        (1, 2): 1.0,
                        (2, 3): 1.5}

    output["residual"] = {3: [1.0, 0.0, 0.0]}

    return output


def cc_out():
    """Static equilibrium results from compression chain."""
    output = {}
    output["xyz"] = {0: [0.0, 0.0, 0.0],
                     1: [1.5, 0.0, 0.0],
                     2: [2.5, 0.0, 0.0],
                     3: [4.0, 0.0, 0.0]}

    output["force"] = {(0, 1): -1.0,
                       (1, 2): -1.0,
                       (2, 3): -1.0}

    output["length"] = {(0, 1): 1.5,
                        (1, 2): 1.0,
                        (2, 3): 1.5}

    output["residual"] = {3: [-1.0, 0.0, 0.0]}

    return output


def tf_out():
    """Static equilibrium results from threebar funicular."""
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
    """Static equilibrium results from braced tower 2d."""
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
                          3: [0.40071844900288345, 0.5384458270605735, -0.0]}
                          # [-0.48639358696951673, 1.0000000124980013, -0.0]

    return output


@pytest.mark.parametrize("topology, output",
                         [(pytest.lazy_fixture("compression_strut"), cs_out()),
                          (pytest.lazy_fixture("threebar_funicular"), tf_out()),
                          (pytest.lazy_fixture("braced_tower_2d"), bt2_out()),
                          (pytest.lazy_fixture("tension_chain"), tc_out()),
                          (pytest.lazy_fixture("compression_chain"), cc_out())
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
                          (pytest.lazy_fixture("braced_tower_2d"), bt2_out()),
                          (pytest.lazy_fixture("tension_chain"), tc_out()),
                          (pytest.lazy_fixture("compression_chain"), cc_out())
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
# Tests - Force Equilibrium Queries
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
