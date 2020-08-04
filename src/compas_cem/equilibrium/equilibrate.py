import numpy as np

from compas.geometry import scale_vector
from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import length_vector


def force_equilibrium(topology, kmax=100, verbose=False):
    """
    Computes force equilibrium at the vertices of the topology diagram.

    Parameters
    ----------
    topology : ``TopologyDiagram``
        A topology diagram
    verbose : ``bool``
        Flag to print out internal operations. Defaults to ``False``.
    *args : ``list``
        Additional arguments
    **kwargs : ``dict``
        Additional keyword arguments
    """

    trails = topology.trails()
    nodes_root_distances(topology, trails)
    w_max = max([len(trail) for trail in trails.values()])

    positions = {}
    trail_vectors = {}

    for k in range(kmax):

        if verbose:
            print("====== Iteration: {} ======".format(k))

        for i in range(w_max):

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
                    t_vec = node_equilibrium(topology, node, t_vec, verbose)
                else:
                    t_vec = node_equilibrium(topology, node, t_vec, True, verbose)

                # if this is the last node, exit
                if i == (len(trail) - 1):
                    continue
                
                # otherwise, pick next node
                next_node = trail[i + 1]
                
                # query trail edge's length and state 
                try:
                    edge = (node, next_node)
                    length, state = topology.edge_attributes(key=edge, names=["length", "state"])
                except KeyError:
                    edge = (next_node, node)
                    length, state = topology.edge_attributes(key=edge, names=["length", "state"])
        
                # add trail vector to node start position
                next_pos = add_vectors(pos, scale_vector(normalize_vector(t_vec), state * length))

                # store new position and trail vector
                positions[next_node] = next_pos
                trail_vectors[next_node] = t_vec
                
                # update node coordinates in topology diagram
                topology.node_attributes(key=next_node, names=["x", "y", "z"], values=next_pos)
                
                # update trail forces in topology diagram
                force = length_vector(t_vec)
                topology.edge_attribute(key=edge, name="force", value=force)
                
                if verbose:
                    print("*****")
                    print("t_vec", t_vec)
                    print("-----")
                    print("length", length)
                    print("state", state)
                    print("pos", pos)
                    print("next_pos", next_pos)

    if verbose:
        print("====== Completed Equilibrium Calculation ======")
        print("\n")
        for key, pos in positions.items():
            print("node: {}, pos: {}".format(key, pos))


def node_equilibrium(topology, node, t_vec, indirect=False, verbose=False):
    """
    Calculates equilibrium at a node using numpy.

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
        Flag to print out internal operations. Defaults to ``False``.
    
    Returns
    -------
    t_vec : ``list``
        The resulting new trail vector.

    """
    tvec_in = scale_vector(t_vec, -1.0)  # incoming trail vector
    q_vec = topology.node_load(node)  # node load
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

    vectors = incoming_edge_vectors(topology, node, deviation_edges)
    states = topology.edges_attribute(name="state", keys=deviation_edges)
    forces = topology.edges_attribute(name="force", keys=deviation_edges)

    for state, force, dev_vec in zip(states, forces, vectors):
        r_vec = add_vectors(r_vec, scale_vector(dev_vec, state * force))

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


def incoming_edge_vectors(topology, node, edges):
    """
    """
    vectors = []
    for u, v in edges:
        other_node = u if u != node else v
        vector = edge_vector(topology, (other_node, node), True)
        vectors.append(vector)

    return vectors


def edge_vector(topology, edge, normalize=False):
    """
    """
    vector = subtract_vectors(*[topology.node_coordinates(n) for n in edge])
    if not normalize:
        return vector
    return normalize_vector(vector)


def nodes_root_distances(topology, trails):
    """
    """
    for _, trail in trails.items():
        for index, node in enumerate(trail):
            topology.node_attribute(node, "_w", index)


if __name__ == "__main__":
    pass
