from compas.geometry import scale_vector
from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector


def force_equilibrium(topology, *args, **kwargs):
    """
    Computes force equilibrium at the vertices of the topology diagram.

    Parameters
    ----------
    topology :: ``TopologyDiagram``
        A topology diagram
    *args : ``list``
        Additional arguments
    **kwargs : ``dict``
        Additional keyword arguments
    """

    trails = topology.trails()
    k_max = max([len(trail) for trail in trails.values()])
    positions = {}
    trail_vectors = {}

    for i in range(k_max):

        for root, trail in trails.items():

            if i > (len(trail) - 1):
                continue

            node = trail[i]

            if i == 0:
                t_vec = [0.0, 0.0, 0.0]
                pos = topology.node_coordinates(root)
            
            else:
                t_vec = trail_vectors[node]
                pos = positions[node]

            print("*****")
            print("t_vec", t_vec)

            t_vec = node_equilibrium(topology, node, t_vec, pos)

            if i == (len(trail) - 1):
                continue
        
            next_node = trail[i + 1]
            
            try:
                edge = (node, next_node)
                length, comb_state = topology.edge_attributes(key=edge, names=["length", "comb_state"])
            except KeyError:
                edge = (next_node, node)
                length, comb_state = topology.edge_attributes(key=edge, names=["length", "comb_state"])

            print("length", length)
            print("comb_state", comb_state)

    
            next_pos = add_vectors(pos, scale_vector(normalize_vector(t_vec), comb_state * length))
            
            print("pos", pos)
            print("next_pos", next_pos)

            positions[next_node] = next_pos
            trail_vectors[next_node] = t_vec
    
    for key, pos in positions.items():
        print("node: {} \t pos: {}".format(key, pos))

        topology.node_attributes(key=key, names=["x", "y", "z"], values=pos)


def node_equilibrium(topology, node, t_vec, pos):
    """
    """
    print("-----")
    print("node", node)

    edges = topology.connected_edges(node)
    q_vec = topology.node_attributes(node, ["qx", "qy", "qz"])
    r_vec = [0.0, 0.0, 0.0]

    print("edges", edges)
    print("qvec", q_vec)

    deviation_edges = [edge for edge in edges if topology.edge_attribute(edge, "type") == "deviation"]
    
    if deviation_edges:
        comb_states = topology.edges_attribute(name="comb_state", keys=deviation_edges)
        forces = topology.edges_attribute(name="force", keys=deviation_edges)

        dev_vectors = []
        # vec_edges = [(node, on) for e in deviation_edges for on in e if on != node]
        vec_edges = [(on, node) for e in deviation_edges for on in e if on != node]
        
        for edge in vec_edges:
            line = [topology.node_coordinates(n) for n in edge]
            vector = normalize_vector(subtract_vectors(*line))
            dev_vectors.append(vector)

        
        print("dev edges", deviation_edges)
        print("comb states", comb_states)
        print("forces", forces)
        print("dev", dev_vectors)

        for comb_state, force, dev_vec in zip(comb_states, forces, dev_vectors):
            r_vec = add_vectors(r_vec, scale_vector(dev_vec, comb_state * force))

    print("r_vec", r_vec)
    
    t_vec = scale_vector(t_vec, -1)
    t_vec_new = subtract_vectors(q_vec, r_vec)
    t_vec_new = subtract_vectors(t_vec, t_vec_new)

    print("t_vec_new", t_vec_new)

    return t_vec_new

if __name__ == "__main__":
    pass