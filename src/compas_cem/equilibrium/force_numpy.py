import autograd.numpy as np

from compas_cem.diagrams import FormDiagram


__all__ = ["static_equilibrium_numpy"]


def static_equilibrium_numpy(topology, tmax=100, eta=1e-5, verbose=False, callback=None):
    """
    Generate a form diagram in static equilibrium using a numpy backend.

    Parameters
    ----------
    topology : ``TopologyDiagram``
        A valid topology diagram
    tmax : ``int``. Optional.
        Maximum number of iterations the algorithm will run for.
        Defaults to ``100``.
    eta: ``float``. Optional.
        Distance threshold that marks equilibrium convergence.
        This threshold is compared against the sum of distances of the nodes'
        positions from one iteration to the next one.
        If ``eta`` is hit before consuming ``kmax`` iterations, calculations
        will stop early. Defaults to ``1e-5``.
    verbose : ``bool``. Optional.
        Flag to print out internal operations. Defaults to ``False``.
    callback : ``function``. Optional.
        An optional callback function to run at every iteration.
    """
    attrs = equilibrium_state_numpy(topology, tmax, eta, verbose, callback)
    form = FormDiagram.from_topology_diagram(topology)
    form_update(form, **attrs)
    return form


def equilibrium_state_numpy(topology, tmax=100, eta=1e-5, verbose=False, callback=None):
    """
    Equilibrate forces in a topology.
    """
    trails = topology.trails()  # calls attribute self.attributes["trails"]

    # input, output
    node_xyz = {n: np.array(topology.node_coordinates(n)) for n in topology.nodes()}

    # output, mutable
    edge_forces = {e: np.array(topology.edge_force(e)) for e in topology.edges()}
    edge_lengths = {e: np.array(topology.edge_attribute(e, "length")) for e in topology.edges()}

    # input, immutable
    # numpy
    node_loads = {n: np.array(topology.node_load(n)) for n in topology.nodes()}
    # no numpy
    node_direct = {n: topology._connected_direct_deviation_edges(n) for n in topology.nodes()}
    node_indirect = {n: topology._connected_indirect_deviation_edges(n) for n in topology.nodes()}
    edge_keys = {e for e in topology.edges()}

    # internals
    trail_vectors = {}

    # output
    reaction_forces = {}
    trail_forces = {}

    for t in range(tmax):  # max iterations

        # store last positions for residual
        last_positions = {k: v for k, v in node_xyz.items()}

        for i in topology.sequences():  # layers

            for _, trail in trails.items():

                # if index is larger than available nodes in trails
                if i > (len(trail) - 1):
                    continue

                # get node key from trail
                node = trail[i]

                # set initial trail vector and position for first iteration
                pos = node_xyz[node]
                if i == 0:
                    t_vec = np.zeros(3)

                # otherwise, select last trail vector and position from dictionary
                else:
                    t_vec = trail_vectors[node]

                # node load
                q_vec = node_loads[node]

                # direct deviation edges vector
                dir_edges = node_direct[node]
                rd_vec = deviation_edges_resultant_vector(node, node_xyz, dir_edges, edge_forces)

                # indirect deviation edges vector
                ri_vec = np.zeros(3)
                if t > 0:
                    indir_edges = node_indirect[node]
                    ri_vec = deviation_edges_resultant_vector(node, node_xyz, indir_edges, edge_forces)

                # node equilibrium, bottleneck 60%
                t_vec = node_equilibrium(t_vec, q_vec, rd_vec, ri_vec)

                # if this is the last node, exit
                if i == (len(trail) - 1):
                    continue

                # otherwise, pick next node in the trail
                next_node = trail[i + 1]

                # correct edge key
                edge = (node, next_node)
                if edge not in edge_keys:
                    edge = (next_node, node)

                # query trail edge's length
                length = edge_lengths[edge]

                trail_force = length_vector(t_vec)
                trail_forces[edge] = trail_force

                next_pos = pos + length * t_vec / trail_force

                # store new position and trail vector
                trail_vectors[next_node] = t_vec

                # store node coordinates
                node_xyz[next_node] = next_pos

                # store reaction force in support node
                reaction_forces[next_node] = t_vec

                # do callback
                if callback:
                    callback()

        # if this is the first iteration, move directly to the next one
        if t == 0:
            continue

        # TODO: simplify by iterating only over values?
        pos_array = np.array([pos for key, pos in node_xyz.items()])
        last_pos_array = np.array([last_positions[key] for key, pos in node_xyz.items()])

        # calculate residual
        residual = np.sqrt(np.sum(np.square(last_pos_array - pos_array)))
        # if residual smaller than threshold, stop iterating
        if residual < eta:
            break

    # if residual larger than threshold after kmax iterations, raise error
    if residual > eta:
        raise ValueError("Over {} iters. residual: {} > eta: {}".format(tmax, residual, eta))

    # print log
    if verbose:
        msg = "====== Completed Equilibrium in {} iters. Residual: {}======"
        print(msg.format(t, residual))

    eq_state = {}
    eq_state["node_xyz"] = node_xyz
    eq_state["trail_forces"] = trail_forces
    eq_state["reaction_forces"] = reaction_forces

    # return node_xyz, trail_forces, reaction_forces
    return eq_state


def form_update(form, node_xyz, trail_forces, reaction_forces):
    """
    Update the node and edge attributes of a form after equilibrating it.
    """
    # assign nodes' coordinates
    for node, xyz in node_xyz.items():
        form.node_attributes(key=node, names=["x", "y", "z"], values=xyz)

    # assign forces on trail edges
    for edge, tforce in trail_forces.items():
        tlength = form.edge_attribute(key=edge, name="length")
        tforce = np.copysign(tforce, tlength)
        form.edge_attribute(key=edge, name="force", value=tforce)

    # assign reaction forces
    for node in form.support_nodes():
        rforce = reaction_forces[node]
        form.node_attributes(key=node, names=["rx", "ry", "rz"], values=rforce)

    # assign lengths to deviation edges
    for u, v in form.edges():
        # length = form.edge_length(u, v)
        length = length_vector(node_xyz[u] - node_xyz[v])
        form.edge_attribute(key=(u, v), name="length", value=length)


def node_equilibrium(t_vec, q_vec, rd_vec, ri_vec):
    """
    Calculates the equilibrium of trail and deviation forces at a node.

    Parameters
    ----------
    t_vec : ``list``
        A trail vector.
    indirect : ``bool``
        Flag to consider indirect deviation edges in the calculation.
        Defaults to ``False``.

    Returns
    -------
    t_vec : ``list``
        The new trail vector.
    """
    tvec_in = -1.0 * t_vec

    return trail_vector_out(tvec_in, q_vec, rd_vec, ri_vec)  # bottleneck


def deviation_edges_resultant_vector(node, node_xyz, deviation_edges, edge_forces):
    """
    Adds up the force vectors of the deviation edges incident to a node.

    Parameters
    ----------
    topology : ``TopologyDiagram``
        A topology diagram.
    node : ``int``
        A node key.
    node_xyz : ``dict``
        A dictionary with node keys and xyz coordinates as values.
    deviation_edges : ``list``
        A list with deviation edges keys.

    Returns
    -------
    rvec : ``list``
        The resulting force vector.
    """
    r_vec = np.zeros(3)
    if not deviation_edges:
        return r_vec

    for edge in deviation_edges:
        force = edge_forces[edge]
        vector = incoming_edge_vector(node, node_xyz, edge, normalize=True)
        r_vec = r_vec + force * vector

    # bottleneck 40%
    # TODO: check if np.array forces broadcasts well with vectors array

    return r_vec


def direct_deviation_edges_resultant_vector(topology, node, node_xyz):
    """
    Adds up the force vectors of the direct deviation edges incident to a node.

    Parameters
    ----------
    topology : ``TopologyDiagram``
        A topology diagram.
    node : ``int``
        A node key.

    Returns
    -------
    rvec : ``list``
        The resulting force vector.
    """
    deviation_edges = topology._connected_direct_deviation_edges(node)
    res = deviation_edges_resultant_vector(topology, node, node_xyz, deviation_edges)

    return res


def indirect_deviation_edges_resultant_vector(topology, node, node_xyz):
    """
    Adds up the force vectors of the indirect deviation edges incident to a node.

    Parameters
    ----------
    topology : ``TopologyDiagram``
        A topology diagram.
    node : ``int``
        A node key.

    Returns
    -------
    rvec : ``list``
        The resulting force vector.
    """
    deviation_edges = topology._connected_indirect_deviation_edges(node)

    return deviation_edges_resultant_vector(topology, node, node_xyz, deviation_edges)


def trail_vector_out(tvec_in, q_vec, rd_vec, ri_vec):
    """
    Calculate an outgoing trail vector.

    Parameters
    ----------
    tvec_in : ``list``
        An incoming trail vector.
    q_vec : ``list``
        A load vector.
    rd_vec : ``list``
        The direct deviation edges resultant force vector.
    ri_vec : ``list``
        The indirect deviation edges resultant force vector.

    Returns
    -------
    tvec_out : ``list``
        An outgoing trail vector.
    """
    return -1.0 * (tvec_in + q_vec + rd_vec + ri_vec)

# ------------------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------------------


def incoming_edge_vectors(node, node_xyz, edges, normalize=False):
    """
    Temporary alternative to Diagram.incoming_edge_vectors()
    """
    vectors = []
    for u, v in edges:
        other = u if u != node else v
        vector = vector_two_nodes(node_xyz[other], node_xyz[node], normalize)
        vectors.append(vector)

    return vectors


def incoming_edge_vector(node, node_xyz, edge, normalize=False):
    """
    Temporary alternative to Diagram.incoming_edge_vectors()
    """
    u, v = edge
    other = u if u != node else v

    return vector_two_nodes(node_xyz[other], node_xyz[node], normalize)


def vector_two_nodes(a, b, normalize=False):
    """
    Calculates the vector between the xyz coordinates of two noddes.

    Parameters
    ----------
    a : ``list``
        The xyz coordinates of the first node
    b : ``list``
        The xyz coordinates of the second node
    normalize : ``bool``
        A boolean flag to normalize all the resulting edge vectors.
        Defaults to ``False``.

    Returns
    -------
    vector : ``list``
        The calculated xyz vector.
    """
    vector = a - b
    if not normalize:
        return vector
    return normalize_vector(vector)


def normalize_vector(vector):
    """
    Hand-made vector normalization.
    """
    return vector / length_vector(vector)


def length_vector(vector):
    """
    Calculates the norm of a vector.
    """
    return np.linalg.norm(vector)


if __name__ == "__main__":
    pass
