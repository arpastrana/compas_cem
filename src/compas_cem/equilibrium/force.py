from math import copysign

from compas.geometry import scale_vector
from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import length_vector
from compas.geometry import distance_point_point

# profiling stuff
import atexit
import line_profiler
profile = line_profiler.LineProfiler()
atexit.register(profile.print_stats)


__all__ = ["force_equilibrium",
           "form_update",
           "form_equilibrate"]


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
    # compute trails
    form.trails()

    # equilibrate form
    attrs = form_equilibrate(form, kmax, eps, verbose, callback)

    # update form node and edge attributes
    form_update(form, *attrs)


# @profile
def form_equilibrate(form, kmax=100, eps=1e-5, verbose=False, callback=None):
    """
    Equilibrate forces in a form.
    """
    trails = form.trails_2()  # calls attribute self.attributes["trails"]
    w_max = max([len(trail) for trail in trails.values()])

    positions = {}
    trail_vectors = {}
    reaction_forces = {}
    trail_forces = {}
    node_xyz = {node: form.node_coordinates(node) for node in form.nodes()}

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
                indirect = True
                if k == 0:
                    indirect = False
                t_vec = node_equilibrium(form, node, t_vec, node_xyz, indirect)

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

                # store node coordinates
                node_xyz[next_node] = next_pos

                # store trail forces
                trail_forces[edge] = copysign(length_vector(t_vec), length)

                # store reaction force in support node
                if form.is_node_support(next_node):
                    reaction_forces[next_node] = t_vec[:]

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
        form.edge_attribute(key=edge, name="force", value=tforce)

    # assign reaction forces
    for node, rforce in reaction_forces.items():
        form.node_attributes(key=node, names=["rx", "ry", "rz"], values=rforce)

    # assign lengths to deviation edges
    for u, v in form.deviation_edges():
        length = form.edge_length(u, v)
        form.edge_attribute(key=(u, v), name="length", value=length)


def node_equilibrium(form, node, t_vec, node_xyz, indirect=False, verbose=False):
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
    rd_vec = direct_deviation_edges_resultant_vector(form, node, node_xyz)

    if indirect:
        ri_vec = indirect_deviation_edges_resultant_vector(form, node, node_xyz)
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
    vector = subtract_vectors(a, b)
    if not normalize:
        return vector
    return normalize_vector(vector)


def deviation_edges_resultant_vector(form, node, node_xyz, deviation_edges):
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
    r_vec = [0.0, 0.0, 0.0]
    if not deviation_edges:
        return r_vec

    # vectors = form.incoming_edge_vectors(node, deviation_edges, True)
    vectors = incoming_edge_vectors(node, node_xyz, deviation_edges, True)
    forces = form.edges_attribute(name="force", keys=deviation_edges)

    for force, dev_vec in zip(forces, vectors):
        r_vec = add_vectors(r_vec, scale_vector(dev_vec, force))

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
    return deviation_edges_resultant_vector(form, node, node_xyz, deviation_edges)


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
    tvec = [0.0, 0.0, 0.0]
    vectors = [tvec_in, q_vec, rd_vec, ri_vec]
    for vec in vectors:
        tvec = add_vectors(tvec, vec)
    return scale_vector(tvec, -1.0)


if __name__ == "__main__":
    pass
