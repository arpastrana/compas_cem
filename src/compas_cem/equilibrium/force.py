from math import copysign

from compas.geometry import scale_vector
from compas.geometry import add_vectors
from compas.geometry import normalize_vector
from compas.geometry import length_vector
from compas.geometry import distance_point_point


__all__ = [
    "force_equilibrium"
]


def force_equilibrium(form, kmax=100, eps=1e-5, verbose=False, callback=None):
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

    trails = form.trails()
    nodes_root_distances(form, trails)


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
                    pos = form.node_coordinates(root)

                # otherwise, select last trail vector and position from dictionary
                else:
                    t_vec = trail_vectors[node]
                    pos = positions[node]

                # calculate nodal equilibrium to get trail direction
                if k == 0:
                    t_vec = node_equilibrium(form, node, t_vec, False)
                else:
                    t_vec = node_equilibrium(form, node, t_vec, True, False)

                # if this is the last node, exit
                if i == (len(trail) - 1):
                    continue

                # otherwise, pick next node in the trail
                next_node = trail[i + 1]

                # query trail edge's length
                try:
                    edge = (node, next_node)
                    length = form.edge_attribute(key=edge, name="length")

                except KeyError:
                    edge = (next_node, node)
                    length = form.edge_attribute(key=edge, name="length")

                next_pos = add_vectors(pos, scale_vector(normalize_vector(t_vec), length))

                # store new position and trail vector
                positions[next_node] = next_pos
                trail_vectors[next_node] = t_vec

                # update node coordinates in topology diagram
                form.node_xyz(key=next_node, xyz=next_pos)

                # update trail forces in topology diagram
                force = copysign(length_vector(t_vec), length)
                form.edge_attribute(key=edge, name="force", value=force)

                # update reaction forces in supports
                nn = next_node
                if form.is_node_support(nn):  # or next_node?
                    attrs = ["rx", "ry", "rz"]
                    form.node_attributes(key=nn, names=attrs, values=t_vec)

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
    for u, v in form.deviation_edges():
        length = form.edge_length(u, v)
        form.edge_attribute(key=(u, v), name="length", value=length)

    # if residual larger than threshold after kmax iterations, raise error
    if residual > eps:
        raise ValueError("Over {} iters. residual: {} > eps: {}".format(kmax, residual, eps))

    if verbose:
        msg = "====== Completed Equilibrium in {} iters. Residual: {}======"
        print(msg.format(k, residual))


def node_equilibrium(form, node, t_vec, indirect=False, verbose=False):
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
    verbose : ``bool``
        Flag to print out internal output. Defaults to ``False``.

    Returns
    -------
    t_vec : ``list``
        The new trail vector.
    """
    tvec_in = scale_vector(t_vec, -1.0)
    q_vec = form.node_load(node)
    rd_vec = direct_deviation_edges_resultant_vector(form, node)

    if indirect:
        ri_vec = indirect_deviation_edges_resultant_vector(form, node)
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


def deviation_edges_resultant_vector(form, node, deviation_edges):
    """
    Adds up the force vectors of the deviation edges incident to a node.

    Parameters
    ----------
    form : ``FormDiagram``
        A form diagram.
    node : ``int``
        A node key.
    deviation_edges : ``list``
        A list with deviation edges keys.

    Returns
    -------
    rvec : ``list``
        The resulting force vector.
    """
    r_vec = [0.0, 0.0, 0.0]
    if not deviation_edges:
        return r_vec

    vectors = form.incoming_edge_vectors(node, deviation_edges, True)
    forces = form.edges_attribute(name="force", keys=deviation_edges)

    for force, dev_vec in zip(forces, vectors):
        r_vec = add_vectors(r_vec, scale_vector(dev_vec, force))

    return r_vec


def direct_deviation_edges_resultant_vector(form, node):
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
    return deviation_edges_resultant_vector(form, node, deviation_edges)


def indirect_deviation_edges_resultant_vector(form, node):
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
    return deviation_edges_resultant_vector(form, node, deviation_edges)


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
    tvec = [0.0, 0.0, 0.0]
    vectors = [tvec_in, q_vec, rd_vec, ri_vec]
    for vec in vectors:
        tvec = add_vectors(tvec, vec)
    return scale_vector(tvec, -1.0)


def nodes_root_distances(form, trails):
    """
    Assigns topological distances to the nodes of the form diagram.

    Parameters
    ----------
    form : ``FormDiagram``
        A form diagram.
    trails : ``dict``
        A dictionary of trails.

    Note
    ----
    This attribute is a helper to find out if an edge is indirect or direct.
    Assignment is made with a private attribute.
    """
    for _, trail in trails.items():
        for index, node in enumerate(trail):
            form.node_attribute(node, "_w", index)


if __name__ == "__main__":
    pass
