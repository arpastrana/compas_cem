import autograd.numpy as np

from compas_cem.diagrams import FormDiagram


__all__ = ["static_equilibrium_numpy"]


def static_equilibrium_numpy(topology, tmax=100, eta=1e-6, verbose=False, callback=None):
    """
    Generate a form diagram in static equilibrium using numpy.

    Parameters
    ----------
    topology : :class:`compas_cem.diagrams.TopologyDiagram`
        A topology diagram.
    tmax : ``int``, optional
        Maximum number of iterations the algorithm will run for.
        Defaults to ``100``.
    eta : ``float``, optional
        Distance threshold that marks equilibrium convergence.
        This threshold is compared against the sum of distances of the nodes'
        positions from one iteration to the next one.
        If ``eta`` is hit before consuming ``tmax`` iterations, calculations
        will stop early.
        Defaults to ``1e-6``.
    verbose : ``bool``, optional
        Flag to print out internal operations.
        Defaults to ``False``.
    callback : ``function``, optional
        An optional callback function to run at every iteration.
        Defaults to ``None``.

    Returns
    -------
    form : :class:`compas_cem.diagrams.FormDiagram`
        A form diagram.
    """
    attrs = equilibrium_state_numpy(topology, tmax, eta, verbose, callback)
    form = FormDiagram.from_topology_diagram(topology)
    form_update(form, **attrs)
    return form


def equilibrium_state_numpy(topology, tmax=100, eta=1e-6, verbose=False, callback=None):
    """
    Equilibrate forces in a topology diagram using numpy.
    """
    # there must be at least one trail
    assert topology.number_of_trails() > 0, "No trails in the diagram!"

    # mapping between trails and sequences, immutable
    trails_sequences = topology.trails_sequences()

    # input, output
    node_xyz = {n: np.array(topology.node_coordinates(n)) for n in topology.nodes()}

    # output, mutable
    edge_forces = {e: np.array(topology.edge_force(e)) for e in topology.edges()}
    edge_lengths = {e: np.array(topology.edge_length_2(e)) for e in topology.edges()}

    # input, immutable
    # numpy
    node_loads = {n: np.array(topology.node_load(n)) for n in topology.nodes()}
    # no numpy
    node_direct = {n: topology._connected_direct_deviation_edges(n) for n in topology.nodes()}
    node_indirect = {n: topology._connected_indirect_deviation_edges(n) for n in topology.nodes()}
    edge_keys = {e for e in topology.edges()}

    # edge planes
    edge_planes = {}
    for edge in topology.trail_edges():
        plane = topology.edge_plane(edge)
        if not plane:
            continue
        plane = [np.array(vector) for vector in plane]
        edge_planes[edge] = plane

    # internals
    residual_vectors = {node: np.array(topology.reaction_force(node)) for node in topology.nodes()}

    # output
    reaction_forces = {}
    trail_forces = {}
    trail_directions = {}

    for t in range(tmax):  # max iterations

        # store last positions for residual
        last_positions = {k: v for k, v in node_xyz.items()}

        for k in range(topology.number_of_sequences()):  # sequences

            for key, trail in topology.trails(keys=True):

                # if index is larger than available nodes in trail, skip trail
                if k not in trails_sequences[key]:
                    continue

                # select node from trail at current sequence
                node = trails_sequences[key][k]

                # get node position
                pos = node_xyz[node]

                # get incoming residual vector
                rvec = residual_vectors[node]

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
                rvec = node_equilibrium(rvec, q_vec, rd_vec, ri_vec)

                # if this is the last node, store and exit
                if topology.is_node_support(node):
                    reaction_forces[node] = rvec
                    continue

                # otherwise, pick next node in the trail
                next_node = trails_sequences[key][k + 1]

                # correct edge key
                edge = (node, next_node)
                if edge not in edge_keys:
                    edge = (next_node, node)

                # query trail edge's length
                length = edge_lengths[edge]

                # query trail edge plane, if any
                plane = edge_planes.get(edge)

                # override length if a plane exists
                if plane:
                    # get length from line plane intersection
                    plength = trail_length_from_plane_intersection_numpy(pos, rvec, plane)

                    # check that returned length is not null
                    if plength:
                        length = plength

                # compute trail force
                trail_force = length_vector_numpy(rvec)  # always positive

                # compute trail direction by normalizing residual vector
                # NOTE: to avoid NaNs, do not normalize residual vector if it is zero length
                nrvec = rvec / trail_force
                if np.isnan(length_vector_numpy(nrvec)):
                    nrvec = rvec

                # store trail direction
                trail_directions[edge] = nrvec

                # store next node position
                next_pos = pos + length * nrvec
                node_xyz[next_node] = next_pos

                # correct trail force sign based on trail signed length
                # NOTE: autograd.np does not support derivatives of copysign
                if trail_force * length < 0.0:
                    trail_force = trail_force * -1.0

                # store trail force
                trail_forces[edge] = trail_force

                # store residual
                residual_vectors[next_node] = rvec

                # do callback
                if callback:
                    callback()

        # if this is the first iteration, move directly to the next one
        if t == 0:
            continue

        # TODO: simplify by iterating only over values?
        pos_array = np.array([pos for key, pos in node_xyz.items()])
        last_pos_array = np.array([last_positions[key] for key, pos in node_xyz.items()])

        # calculate residual distance
        distance = np.sqrt(np.sum(np.square(last_pos_array - pos_array)))
        # if residual distance smaller than threshold, stop iterating
        if distance < eta:
            break

    # if residual distance larger than threshold after tmax iterations, raise error
    if t > 0:
        if distance > eta:
            raise ValueError("Over {} iters. Residual: {} > eta: {}".format(tmax, distance, eta))

    # print log
    if verbose:
        msg = "====== Completed Equilibrium in {} iters. Residual: {}======"
        print(msg.format(t, distance))

    eq_state = {}
    eq_state["node_xyz"] = node_xyz
    eq_state["trail_forces"] = trail_forces
    eq_state["trail_directions"] = trail_directions
    eq_state["reaction_forces"] = reaction_forces

    # return node_xyz, trail_forces, reaction_forces
    return eq_state


def form_update(form, node_xyz, trail_forces, reaction_forces, **kwargs):
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
        rforce = reaction_forces[node]
        form.node_attributes(key=node, names=["rx", "ry", "rz"], values=rforce)

    # assign lengths to deviation edges
    for edge in form.edges():
        u, v = edge
        length = length_vector_numpy(node_xyz[u] - node_xyz[v])
        force = form.edge_attribute(key=edge, name="force")
        length = np.copysign(length, force)
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
    return normalize_vector_numpy(vector)


def normalize_vector_numpy(vector):
    """
    Hand-made vector normalization.
    """
    return vector / length_vector_numpy(vector)


def length_vector_numpy(vector):
    """
    Calculates the norm of a vector.
    """
    return np.linalg.norm(vector)


def trail_length_from_plane_intersection_numpy(point, vector, plane, tol=1e-6):
    """
    Calculates the signed length of a trail edge from a vector-plane intersection.

    Parameters
    ----------
    point : ``list`` of ``float``
        The XYZ coordinates of the base position of the vector.
    direction : ``list`` of ``float``
        The XYZ coordinates of the vector.
    plane : ``Plane``
        A COMPAS plane defined by a base point and a normal vector.
    tol : ``float``, optional
        A tolerance to check if vector and the plane normal are parallel
        Defaults to ``1e-6``.

    Returns
    -------
    length : ``float``, ``None``
        The distance between ``pos`` and the resulting line-plane intersection.
        If not intersection is found, it returns ``None``.
    """
    origin, normal = plane
    cos_nv = np.dot(normal, normalize_vector_numpy(vector))

    if np.abs(cos_nv) < tol:
        return

    oa = origin - point
    cos_noa = np.dot(normal, oa)

    return cos_noa / cos_nv


if __name__ == "__main__":
    pass
