from compas.geometry import scale_vector
from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import length_vector
from compas.geometry import distance_point_point

from math import copysign

__all__ = [
    "force_equilibrium"
]


def force_equilibrium(topology, kmax=100,  eps=1e-5, verbose=False, callback=None):
    """
    Computes force equilibrium on the vertices of the topology diagram.

    Parameters
    ----------
    topology : ``TopologyDiagram``
        A topology diagram
    kmax : ``int``. Optional.
        Maximum number of iterations the algorithm will run for.
        Defaults to ``100``.
    eps : ``float``. Optional.
        Distance threshold that marks equilibrium convergence.
        This threshold is compared against the sum of distances of the nodes'
        positions from one iteration to the next one.
        If ``eps`` is hit before consuming ``kmax`` iterations, calculations
        will stop early. Defaults to ``1e-5``.
    verbose : ``bool``. Optional.
        Flag to print out internal operations. Defaults to ``False``.
    callback : ``function``. Optional.
        An optional callback function to run at every iteration.
    """

    trails = topology.trails()
    nodes_root_distances(topology, trails)
    w_max = max([len(trail) for trail in trails.values()])

    positions = {}
    trail_vectors = {}

    for k in range(kmax):  # max iterations

        # store last positions for residual
        last_positions = {k: v for k, v in positions.items()}

        for i in range(w_max):  # layers

            for root, trail in trails.items():

                # if index is larger than available nodes in trails
                if i > (len(trail) - 1):
                    continue

                # select node from trail
                node = trail[i]

                # set initial trail vector and position for first iteration
                if i == 0:
                    t_vec = [0.0, 0.0, 0.0]
                    pos = topology.node_coordinates(root)
                
                # otherwise, select last trail vector and position from dictionary
                else:
                    t_vec = trail_vectors[node]
                    pos = positions[node]

                # calculate nodal equilibrium to get trail direction
                if k == 0:
                    t_vec = node_equilibrium(topology, node, t_vec, False)
                else:
                    t_vec = node_equilibrium(topology, node, t_vec, True, False)

                # if this is the last node, exit
                if i == (len(trail) - 1):
                    continue
                
                # otherwise, pick next node in the trail
                next_node = trail[i + 1]
                
                # query trail edge's length
                try:
                    edge = (node, next_node)
                    length = topology.edge_attribute(key=edge, name="length")
                except KeyError:
                    edge = (next_node, node)
                    length = topology.edge_attribute(key=edge, name="length")
        
                # add trail vector to node start position
                next_pos = add_vectors(pos, scale_vector(normalize_vector(t_vec), length))

                # store new position and trail vector
                positions[next_node] = next_pos
                trail_vectors[next_node] = t_vec
                
                # update node coordinates in topology diagram
                topology.node_attributes(key=next_node, names=["x", "y", "z"], values=next_pos)
                
                # update trail forces in topology diagram
                force = copysign(length_vector(t_vec), length)
                topology.edge_attribute(key=edge, name="force", value=force)

                # do callback
                if callback:
                    callback()

        # if this is the first iteration, move directly to the next one
        if k == 0:
            continue

        # calculate residual
        residual = 0.0
        for key, pos in positions.items():
            last_pos = last_positions[key]
            residual += distance_point_point(last_pos, pos)

        # if residual smaller than threshold, stop iterating
        if residual < eps:
            break

    # assign lengths to deviation edges
    for u, v in topology.deviation_edges():
        length = topology.edge_length(u, v)
        topology.edge_attribute(key=(u, v), name="length", value=length)

    # if residual smaller than threshold, stop iterating
    if residual > eps:
        raise ValueError("Over {} iters. residual: {} > eps: {}".format(kmax, residual, eps))
    
    # TODO: assign reaction forces at supports

    if verbose:
        msg = "====== Completed Equilibrium in {} iters. Residual: {}======"
        print(msg.format(k, residual))
        print("\n")


def node_equilibrium(topology, node, t_vec, indirect=False, verbose=False):
    """
    Calculates equilibrium of trail and deviation forces at a node.

    Parameters
    ----------
    topology : ``TopologyDiagram``
        A topology diagram
    node : ``int``
        A node key.
    t_vec : ``list``
        A trail vector.
    indirect : ``bool``
        Flag to consider indirect deviation edges in the calculation.
        Defaults to ``False``.
    verbose : ``bool``
        Flag to print out internal output. Defaults to ``False``.
    
    Returns
    -------
    t_vec : ``list``
        The resulting new trail vector.

    """
    tvec_in = scale_vector(t_vec, -1.0)
    q_vec = topology.node_load(node)
    rd_vec = direct_deviation_edges_resultant_vector(topology, node)

    if indirect:
        ri_vec = indirect_deviation_edges_resultant_vector(topology, node)
    else:
        ri_vec = [0.0, 0.0, 0.0]

    tvec_out = trail_vector_out(tvec_in, q_vec, rd_vec, ri_vec)

    if verbose:
        print("-----")
        print("node", node)
        print("qvec", q_vec)
        print("rd_vec", rd_vec)
        print("ri_vec", rd_vec)
        print("t vec np", tvec_out)

    return tvec_out


def deviation_edges_resultant_vector(topology, node, deviation_edges):
    """
    """
    r_vec = [0.0, 0.0, 0.0]
    if not deviation_edges:
        return r_vec

    vectors = topology.incoming_edge_vectors(node, deviation_edges, True)
    forces = topology.edges_attribute(name="force", keys=deviation_edges)

    for force, dev_vec in zip(forces, vectors):
        r_vec = add_vectors(r_vec, scale_vector(dev_vec, force))

    return r_vec


def direct_deviation_edges_resultant_vector(topology, node):
    """
    """
    deviation_edges = topology._connected_direct_deviation_edges(node)
    return deviation_edges_resultant_vector(topology, node, deviation_edges)


def indirect_deviation_edges_resultant_vector(topology, node):
    """
    """
    deviation_edges = topology._connected_indirect_deviation_edges(node)
    return deviation_edges_resultant_vector(topology, node, deviation_edges)


def trail_vector_out(tvec_in, q_vec, rd_vec, ri_vec):
    """
    """
    tvec = [0.0, 0.0, 0.0]
    vectors = [tvec_in, q_vec, rd_vec, ri_vec]
    for vec in vectors:
        tvec = add_vectors(tvec, vec)
    return scale_vector(tvec, -1.0)


def nodes_root_distances(topology, trails):
    """
    """
    for _, trail in trails.items():
        for index, node in enumerate(trail):
            topology.node_attribute(node, "_w", index)


if __name__ == "__main__":
    pass
