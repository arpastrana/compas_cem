import numpy as np

from compas.geometry import scale_vector
from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector


def force_equilibrium(topology, verbose=False, *args, **kwargs):
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
    assign_topological_distances(topology, trails)

    k_max = max([len(trail) for trail in trails.values()])
    positions = {}
    trail_vectors = {}

    for i in range(k_max):

        for root, trail in trails.items():

            # if index is larger than available nodes in trails
            if i > (len(trail) - 1):
                continue

            node = trail[i]

            if i == 0:
                t_vec = [0.0, 0.0, 0.0]
                pos = topology.node_coordinates(root)
            
            else:
                t_vec = trail_vectors[node]
                pos = positions[node]

            t_vec = node_equilibrium_numpy(topology, node, t_vec, pos, verbose)

            if i == (len(trail) - 1):
                continue
        
            next_node = trail[i + 1]
            
            try:
                edge = (node, next_node)
                length, state = topology.edge_attributes(key=edge, names=["length", "state"])
            except KeyError:
                edge = (next_node, node)
                length, state = topology.edge_attributes(key=edge, names=["length", "state"])
    
            next_pos = add_vectors(pos, scale_vector(normalize_vector(t_vec), state * length))

            positions[next_node] = next_pos
            trail_vectors[next_node] = t_vec
            
            topology.node_attributes(key=next_node, names=["x", "y", "z"], values=next_pos)
            
            if verbose:
                print("*****")
                print("t_vec", t_vec)
                print("-----")
                print("length", length)
                print("state", state)
                print("pos", pos)
                print("next_pos", next_pos)

    if verbose:
        for key, pos in positions.items():
            print("node: {}, pos: {}".format(key, pos))


def node_equilibrium_numpy(topology, node, t_vec, pos, verbose=False):
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
    pos : ``list``
        An xyz position vector.
    verbose : ``bool``
        Flag to print out internal operations. Defaults to ``False``.
    
    Returns
    -------
    t_vec : ``list``
        The resulting new trail vector.

    """
    t_vec = np.array(t_vec) * -1  # trail vector
    q_vec = np.array(topology.node_attributes(node, ["qx", "qy", "qz"]))  # load
    r_vec = residual_deviation_vector_numpy(topology, node)  # deviation edges 

    tvec_out = trail_vector_out_numpy(t_vec, r_vec, q_vec)
    tvec_out = tvec_out.tolist()

    if verbose:
        print("-----")
        print("node", node)
        print("edges", edges)
        print("qvec", q_vec)
        print("r_vec", r_vec)
        print("t vec np", tvec_np)

    return tvec_out


def residual_deviation_vector_numpy(topology, node):
    """
    """
    r_vec = np.zeros(3)

    deviation_edges = topology.connected_deviation_edges(node)

    if not deviation_edges:
        return r_vec

    vectors = incoming_edge_vectors(topology, node, deviation_edges)
    states = topology.edges_attribute(name="state", keys=deviation_edges)
    forces = topology.edges_attribute(name="force", keys=deviation_edges)
    
    for state, force, dev_vec in zip(states, forces, vectors):
        r_vec += state * force * dev_vec

    return r_vec


def trail_vector_out_numpy(t_vec, r_vec, q_vec):
    """
    """
    tvec_np = - np.array(t_vec) - np.array(r_vec) - np.array(q_vec)
    return tvec_np


def incoming_edge_vectors(topology, node, edges):
    """
    """
    vectors = []

    for u, v in edges:
        other_node = u if u != node else v
        vector = edge_vector_numpy(topology, (other_node, node), normalize=True)
        vectors.append(vector)

    return vectors


def edge_vector_numpy(topology, edge, normalize=False):
    """
    """
    line = [topology.node_coordinates(n) for n in edge]
    vector = np.array(line[0]) - np.array(line[1])
    if normalize:
        vector = vector / np.linalg.norm(vector)

    return vector


def assign_topological_distances(topology, trails):
    """
    """
    for _, trail in trails.items():
        for index, node in enumerate(trail):
            topology.node_attribute(node, "_w", index)


def node_equilibrium(topology, node, t_vec, pos, verbose=False):
    """
    Calculates equilibrium at a node.

    Parameters
    ----------
    topology : ``TopologyDiagram``
        A topology diagram
    node : ``int``
        A node key.
    t_vec : ``list``
        A trail vector.
    pos : ``list``
        An xyz position vector.
    verbose : ``bool``
        Flag to print out internal operations. Defaults to ``False``.

    Returns
    -------
    t_vec : ``list``
        The resulting new trail vector.
    """
    t_vec = scale_vector(t_vec, -1)
    r_vec = [0, 0, 0]
    q_vec = topology.node_attributes(node, ["qx", "qy", "qz"])
    edges = topology.connected_edges(node)

    deviation_edges = [edge for edge in edges if topology.edge_attribute(edge, "type") == "deviation"]
    
    if deviation_edges:
        states = topology.edges_attribute(name="state", keys=deviation_edges)
        forces = topology.edges_attribute(name="force", keys=deviation_edges)

        dev_vectors = []
        vec_edges = [(on, node) for e in deviation_edges for on in e if on != node]
        
        for edge in vec_edges:
            line = [topology.node_coordinates(n) for n in edge]
            vector = normalize_vector(subtract_vectors(*line))
            dev_vectors.append(vector)

        if verbose:
            print("dev edges", deviation_edges)
            print("comb states", states)
            print("forces", forces)
            print("dev", dev_vectors)

        for state, force, dev_vec in zip(states, forces, dev_vectors):
            r_vec = add_vectors(r_vec, scale_vector(dev_vec, state * force))
    
    t_vec_new = subtract_vectors(r_vec, q_vec)
    t_vec_new = subtract_vectors(t_vec_new, scale_vector(t_vec, -1))

    if verbose:
        print("-----")
        print("node", node)
        print("edges", edges)
        print("qvec", q_vec)
        print("r_vec", r_vec)
        print("t vec new", t_vec_new)

    return t_vec_new


if __name__ == "__main__":
    pass