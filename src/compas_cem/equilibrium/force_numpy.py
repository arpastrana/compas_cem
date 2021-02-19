import jax.numpy as np

# profiling stuff
import atexit
import line_profiler
profile = line_profiler.LineProfiler()
atexit.register(profile.print_stats)


__all__ = ["force_equilibrium_numpy",
           "form_update",
           "form_equilibrate"]


def force_equilibrium_numpy(form, kmax=100, eps=1e-5, verbose=False):
    """
    Computes force equilibrium on the nodes of the force diagram.

    Parameters
    ----------
    form : ``FormDiagram``
        A form diagram
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
    # compute trails
    # form.trails()

    # equilibrate form
    attrs = form_equilibrate(form, kmax, eps, verbose)  # bottleneck

    # update form node and edge attributes
    form_update(form, *attrs)


@profile
def form_equilibrate(form, kmax=100, eps=1e-5, verbose=False):
    """
    Equilibrate forces in a form.
    """
    trails = form.trails_2()  # calls attribute self.attributes["trails"]
    w_max = max([len(trail) for trail in trails.values()])

    # positions = {}
    trail_vectors = {}
    reaction_forces = {}
    trail_forces = {}

    # dict arrays
    node_xyz = {n: np.array(form.node_coordinates(n)) for n in form.nodes()}
    node_loads = {n: np.array(form.node_load(n)) for n in form.nodes()}
    node_residuals = {n: np.array(form.node_residual(n)) for n in form.nodes()}

    node_direct = {n: form._connected_direct_deviation_edges(n) for n in form.nodes()}
    node_indirect = {n: form._connected_indirect_deviation_edges(n) for n in form.nodes()}

    edge_keys = {e for e in form.edges()}

    edge_forces = {e: np.array(form.edge_force(e)) for e in form.edges()}
    edge_lengths = {e: np.array(form.edge_attribute(e, "length")) for e in form.edges()}

    # create index key dictionaries for nodes and edges
    # node_index = form.key_index()
    # edge_index = form.uv_index()

    # indirect edges not considered until second k iteration

    for k in range(kmax):  # max iterations

        # store last positions for residual
        # last_positions = {k: v for k, v in positions.items()}
        last_positions = {k: v for k, v in node_xyz.items()}

        for i in range(w_max):  # layers

            for root, trail in trails.items():

                # if index is larger than available nodes in trails
                if i > (len(trail) - 1):
                    continue

                # get node key from trail
                node = trail[i]

                # set initial trail vector and position for first iteration
                pos = node_xyz[node]
                if i == 0:
                    t_vec = np.zeros(3)
                    # pos = form.node_coordinates(root)
                    # pos = node_xyz[root]  #jax array

                # otherwise, select last trail vector and position from dictionary
                else:
                    t_vec = trail_vectors[node]
                    # pos = positions[node]
                    # pos = node_xyz[node]

                # node load
                q_vec = node_loads[node]

                # direct deviation edges vector
                dir_edges = node_direct[node]
                rd_vec = deviation_edges_resultant_vector(node, node_xyz, dir_edges, edge_forces)

                # indirect deviation edges vector
                ri_vec = np.zeros(3)
                if k > 0:
                    indir_edges = node_indirect[node]
                    ri_vec = deviation_edges_resultant_vector(node, node_xyz, indir_edges, edge_forces)

                # node equilibrium, bottleneck 60%
                t_vec = node_equilibrium(form, node, t_vec, q_vec, rd_vec, ri_vec)

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

                # try:
                #     edge = (node, next_node)
                #     length = form.edge_attribute(key=edge, name="length")

                # except KeyError:
                #     edge = (next_node, node)
                #     length = form.edge_attribute(key=edge, name="length")
                # store trail forces
                # trail_forces[edge] = copysign(length_vector(t_vec), length)
                trail_force = length_vector(t_vec)
                # bottleneck 10%
                # trail_forces[edge] = np.copysign(trail_force, length)
                trail_forces[edge] = trail_force

                # bottleneck 20%
                # next_pos = add_vectors(pos, scale_vector(normalize_vector(t_vec), length))
                # next_pos = np.array(pos) + length * normalize_vector(t_vec)
                # next_pos = pos + length * normalize_vector(t_vec)
                next_pos = pos + length * t_vec / trail_force

                # store new position and trail vector
                # positions[next_node] = next_pos
                trail_vectors[next_node] = t_vec

                # store node coordinates
                node_xyz[next_node] = next_pos


                # store reaction force in support node
                # if form.is_node_support(next_node):
                reaction_forces[next_node] = t_vec

                # do callback
                # if callback:
                #     callback()

        # if this is the first iteration, move directly to the next one
        if k == 0:
            continue

        # calculate residual
        # residual = 0.0
        # TODO: simplify by iterating only over values?
        # pos_array = np.array([pos for key, pos in positions.items()])
        # last_pos_array = np.array([last_positions[key] for key, pos in positions.items()])
        # residual = np.sqrt(np.sum(np.square(last_pos_array - pos_array)))

        pos_array = np.array([pos for key, pos in node_xyz.items()])
        last_pos_array = np.array([last_positions[key] for key, pos in node_xyz.items()])
        residual = np.sqrt(np.sum(np.square(last_pos_array - pos_array)))
        # for key, pos in positions.items():
        #     last_pos = last_positions[key]
            # residual += distance_point_point(last_pos, pos)
            # if isinstance(pos, list):
            #     pos = np.array(pos)
            # if isinstance(last_pos, list):
            #     last_pos = np.array(last_pos)

            # residual += np.sum(np.square(np.subtract(last_pos, pos)))

        # if residual smaller than threshold, stop iterating
        if residual < eps:
            break

    # if residual larger than threshold after kmax iterations, raise error
    if residual > eps:
        raise ValueError("Over {} iters. residual: {} > eps: {}".format(kmax, residual, eps))

    # print log
    if verbose:
        msg = "====== Completed Equilibrium in {} iters. Residual: {}======"
        print(msg.format(k, residual))

    return node_xyz, trail_forces, reaction_forces


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
    for node, rforce in reaction_forces.items():
        form.node_attributes(key=node, names=["rx", "ry", "rz"], values=rforce)

    # assign lengths to deviation edges
    for u, v in form.deviation_edges():
        # length = form.edge_length(u, v)
        length = length_vector(node_xyz[u] - node_xyz[v])
        form.edge_attribute(key=(u, v), name="length", value=length)


@profile
def node_equilibrium(form, node, t_vec, q_vec, rd_vec, ri_vec):
    """
    Calculates the equilibrium of trail and deviation forces at a node.

    Parameters
    ----------
    form : ``FormDiagram``
        A form diagram
    node : ``int``
        A node key.
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
    # tvec_in = scale_vector(t_vec, -1.0)
    # q_vec = form.node_load(node)
    # breakpoint()

    # rd_vec = direct_deviation_edges_resultant_vector(form, node, node_xyz)  # bottleneck

    # ri_vec = np.zeros(3)
    # if indirect:
    #     ri_vec = indirect_deviation_edges_resultant_vector(form, node, node_xyz)

    tvec_out = trail_vector_out(tvec_in, q_vec, rd_vec, ri_vec)  # bottleneck

    return tvec_out

@profile
def deviation_edges_resultant_vector(node, node_xyz, deviation_edges, edge_forces):
    """
    Adds up the force vectors of the deviation edges incident to a node.

    Parameters
    ----------
    form : ``FormDiagram``
        A form diagram.
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
    # r_vec = [0.0, 0.0, 0.0]
    r_vec = np.zeros(3)
    if not deviation_edges:
        return r_vec
        # return np.zeros(3)

    # vectors = form.incoming_edge_vectors(node, deviation_edges, True)

    # bottleneck 60%
    # forces = form.edges_attribute(name="force", keys=deviation_edges)
    # vectors = incoming_edge_vectors(node, node_xyz, deviation_edges, True)
    #
    for edge in deviation_edges:
        force = edge_forces[edge]
        vector = incoming_edge_vector(node, node_xyz, edge, normalize=True)
        r_vec = r_vec + force * vector

    # bottleneck 40%
    # TODO: check if np.array forces broadcasts well with vectors array
    # vectors = np.multiply(np.array(forces), np.array(vectors))

    #
    # r_vec = np.sum(vectors, axis=0)

    # for force, dev_vec in zip(forces, vectors):
    #     r_vec = add_vectors(r_vec, scale_vector(dev_vec, force))

    return r_vec


def direct_deviation_edges_resultant_vector(form, node, node_xyz):
    """
    Adds up the force vectors of the direct deviation edges incident to a node.

    Parameters
    ----------
    form : ``FormDiagram``
        A form diagram.
    node : ``int``
        A node key.

    Returns
    -------
    rvec : ``list``
        The resulting force vector.
    """
    deviation_edges = form._connected_direct_deviation_edges(node)


    res = deviation_edges_resultant_vector(form, node, node_xyz, deviation_edges)

    return res


def indirect_deviation_edges_resultant_vector(form, node, node_xyz):
    """
    Adds up the force vectors of the indirect deviation edges incident to a node.

    Parameters
    ----------
    form : ``FormDiagram``
        A form diagram.
    node : ``int``
        A node key.

    Returns
    -------
    rvec : ``list``
        The resulting force vector.
    """
    deviation_edges = form._connected_indirect_deviation_edges(node)

    return deviation_edges_resultant_vector(form, node, node_xyz, deviation_edges)


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
    # tvec = [0.0, 0.0, 0.0]
    # vectors = [tvec_in, q_vec, rd_vec, ri_vec]
    # for vec in vectors:
    #     tvec = add_vectors(tvec, vec)
    # return scale_vector(tvec, -1.0)

    # vectors = np.array([tvec_in, q_vec, rd_vec, ri_vec])  # bottleneck
    # vectors = np.vstack([tvec_in, q_vec, rd_vec, ri_vec])
    # result =  -1.0 * np.sum(vectors, axis=0)

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

    return  vector_two_nodes(node_xyz[other], node_xyz[node], normalize)


@profile
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
    # vector = subtract_vectors(a, b)
    # if isinstance(a, list):
    #     a = np.array(a)
    # if isinstance(b, list):
    #     b = np.array(b)
    vector = a - b
    if not normalize:
        return vector
    return normalize_vector(vector)


def normalize_vector(vector):
    # if isinstance(vector, list):
    #     vector = np.array(vector)
    return vector / length_vector(vector)


def length_vector(vector):
    # if isinstance(vector, list):
    #     vector = np.array(vector)
    return np.linalg.norm(vector)


if __name__ == "__main__":
    pass
