from compas.geometry import distance_point_point

from compas.utilities import pairwise

from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.elements import DeviationEdge

from compas_cem.supports import NodeSupport


__all__ = ["MeshMixins"]


# ==============================================================================
# Mesh Mixins
# ==============================================================================

class MeshMixins(object):
    @classmethod
    def from_dualquadmesh(cls, mesh, supports, trail_length=None, trail_state=-1, deviation_force=1.0, deviation_state=-1):
        """
        Generate a topology diagram from the dual of a quad mesh.

        Inputs
        ------
        mesh : QuadMesh
            The dual of a quad mesh.
        supports : list
            The list of vertex indices in the mesh that represent supports.
        trail_length : `float`, optional
            The length of all the trail edges.
            If `None`, then the trail edges inherit their length from the input mesh.
            Defaults to `None`.
        trail_state : `int`, optional
            The internal force state of the trail edges.
            A value of `-1` means compression and `1`, tension.
            Defaults to `-1`.
        deviation_force : `float`, optional
            The force in all the deviation edges.
            Defaults to `1.0`.
        deviation_state : `int`, optional
            The internal force state of the deviation edges.
            A value of `-1` means compression and `1`, tension.
            Defaults to `-1`.

        Returns
        -------
        diagram : TopologyDiagram
            The topology diagram.
        """

        mesh.collect_polyedges()

        supports = set(supports)

        trail = []
        deviation = []

        for pkey, polyedge in mesh.polyedges(data=True):

            start, end = polyedge[0], polyedge[-1]

            # TODO: closed polyedge (TO TEST/FIX)
            if start == end:
                deviation.extend(list(pairwise(polyedge)))

            # open polyedge
            else:
                # no supports at polyedge extremities
                if start not in supports and end not in supports:
                    deviation.extend(list(pairwise(polyedge)))

                # supports at both polyedge extremities
                elif start in supports and end in supports:

                    if polyedge[1] in supports:
                        continue

                    n = int(len(polyedge) / 2) - 1

                    # central edge becomes deviation
                    deviation.append(tuple(polyedge[n: n + 2]))

                    # rest splits into two trails
                    trail.extend(list(pairwise(polyedge[:n + 1])))
                    trail.extend(list(pairwise(polyedge[n + 1:])))

                # unique support at polyedge extremities
                else:
                    trail.extend(list(pairwise(polyedge)))

        topology = cls()

        for vkey in mesh.vertices():
            topology.add_node(Node(key=vkey, xyz=mesh.vertex_coordinates(vkey)))

        for vkey in supports:
            topology.add_support(NodeSupport(vkey))

        for edge in deviation:
            force = deviation_state * deviation_force
            topology.add_edge(DeviationEdge(*edge, force=force))

        for edge in trail:

            if trail_length:
                signed_length = trail_length * trail_state
            else:
                edge_coordinates = [topology.node_coordinates(node) for node in edge]
                assert len(edge_coordinates) == 2
                signed_length = distance_point_point(*edge_coordinates) * trail_state

            topology.add_edge(TrailEdge(*edge, length=signed_length))

        return topology
