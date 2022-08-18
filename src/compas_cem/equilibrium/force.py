from math import copysign
from math import fabs

from compas.geometry import dot_vectors
from compas.geometry import scale_vector
from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import length_vector
from compas.geometry import distance_point_point
from compas.geometry import intersection_line_plane

from compas_cem.diagrams import FormDiagram


__all__ = ["static_equilibrium"]


SMALL_VALUE = 1e-3


def static_equilibrium(topology, tmax=100, eta=1e-6, verbose=False, callback=None):
    """
    Generate a form diagram in static equilibrium.

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
    attrs = equilibrium_state(topology, tmax, eta, verbose, callback)
    form = FormDiagram.from_topology_diagram(topology)
    form_update(form, **attrs)
    return form


def equilibrium_state(topology, tmax=100, eta=1e-6, verbose=False, callback=None):
    """
    Equilibrate forces at the nodes of a topology diagram.
    """
    trails = list(topology.trails())

    # there must be at least one trail
    assert len(trails) != 0, "No trails in the diagram!"

    # positions = {}
    residual_vectors = {}
    reaction_forces = {}
    trail_forces = {}
    node_xyz = {node: topology.node_coordinates(node) for node in topology.nodes()}

    for t in range(tmax):  # max iterations

        # store last positions for residual
        last_xyz = {k: v for k, v in node_xyz.items()}

        for i in topology.sequences():  # sequences

            for trail in trails:

                # if index is larger than available nodes in trails
                if i > (len(trail) - 1):
                    continue

                # select node from trail
                node = trail[i]

                # set initial trail vector and position for first iteration
                pos = node_xyz[node]
                if i == 0:
                    rvec = [0.0, 0.0, 0.0]

                # otherwise, select last trail vector and position from dictionary
                else:
                    rvec = residual_vectors[node]

                # calculate nodal equilibrium to get new residual vector
                indirect = True
                if t == 0:
                    indirect = False
                rvec = node_equilibrium(topology, node, rvec, node_xyz, indirect)

                # if this is the last node, store reaction force and exit loop
                if topology.is_node_support(node):
                    reaction_forces[node] = rvec[:]
                    continue

                # otherwise, pick next node in the trail
                next_node = trail[i + 1]

                # correct edge key
                edge = (node, next_node)
                if not topology.has_edge(*edge):
                    edge = (next_node, node)

                # query trail edge length
                length = topology.edge_attribute(key=edge, name="length")

                # query trail edge plane, it takes precedence over length
                plane = topology.edge_attribute(key=edge, name="plane")

                # override signed length if a plane has been supplied for trail edge
                if plane:
                    # compute length from line plane intersection
                    plength = trail_length_from_plane_intersection(pos, rvec, plane)
                    # The intersection length is None or zero
                    if not plength:
                        msg = "Warning! No intersection found between vector {} of edge {} and plane {}"
                        print(msg.format(rvec, edge, plane))
                        print("Falling back to input length: {}".format(length))
                    #  valid intersection length exists
                    else:
                        # print out warning if there is a swipe in the force state of the edge
                        if plength * length < 0.:
                            print("Warning! Force state has flipped for edge {} due to plane intersection".format(edge))
                        # print out warning if zero length
                        if fabs(plength) < SMALL_VALUE:
                            msg = "Warning! Length for edge {} after intersection is {}."
                            print(msg.format(edge, length), "Check the plane.")
                        # override signed length
                        length = plength

                # store next node position
                next_pos = add_vectors(pos, scale_vector(normalize_vector(rvec), length))
                node_xyz[next_node] = next_pos

                # store trail force
                trail_forces[edge] = copysign(length_vector(rvec), length)

                # store residual vector
                residual_vectors[next_node] = rvec

                # do callback
                if callback:
                    callback()

        # if this is the first iteration, move directly to the next one
        if t == 0:
            continue

        # calculate residual
        residual = 0.0
        for key, pos in node_xyz.items():
            last_pos = last_xyz[key]
            residual += distance_point_point(last_pos, pos)

        # if residual smaller than threshold, stop iterating
        if residual < eta:
            break

    # if residual larger than threshold after tmax iterations, raise error
    if t > 0:
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

    return eq_state


def form_update(form, node_xyz, trail_forces, reaction_forces):
    """
    Update the node and edge attributes of a form after equilibrating it.
    """
    # assign nodes' coordinates
    for node, xyz in node_xyz.items():
        form.node_xyz(node, xyz)
        # form.node_attributes(key=node, names=["x", "y", "z"], values=xyz)

    # assign forces on trail edges
    for edge, tforce in trail_forces.items():
        # tlength = form.edge_attribute(key=edge, name="length")
        # tforce = copysign(tforce, tlength)
        form.edge_attribute(key=edge, name="force", value=tforce)

    # assign reaction forces
    for node, rforce in reaction_forces.items():
        form.node_attributes(key=node, names=["rx", "ry", "rz"], values=rforce)

    # assign lengths to deviation edges
    for u, v in form.edges():
        length = form.edge_length(u, v)
        force = form.edge_attribute(key=edge, name="force")
        length = copysign(length, force)
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


def trail_length_from_plane_intersection(point, vector, plane, tol=1e-6):
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
    cos_nv = dot_vectors(normal, normalize_vector(vector))

    if fabs(cos_nv) < tol:
        return

    oa = subtract_vectors(origin, point)
    cos_noa = dot_vectors(normal, oa)

    return cos_noa / cos_nv


if __name__ == "__main__":
    pass
