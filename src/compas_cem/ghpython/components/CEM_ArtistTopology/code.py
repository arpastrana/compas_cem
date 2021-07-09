"""
Draw a topology diagram.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.ghpython import TopologyArtist


class TopologyArtistComponent(component):
    def RunScript(self, topology, node, edge, load_min, load_scale):
        node = node or None
        edge = edge or None
        load_min = load_min or 1e-3
        load_scale = load_scale or 1.0
        if topology:
            artist = TopologyArtist(topology)

            nodes = artist.draw_nodes(node)
            origin_nodes = artist.draw_nodes_origin(node)
            support_nodes = artist.draw_nodes_support(node)

            edges = artist.draw_edges(edge)
            trail_edges = artist.draw_edges_trail(edge)
            deviation_edges = artist.draw_edges_deviation(edge)

            loads = artist.draw_loads(node, min_load=load_min, scale=load_scale)

            return nodes, origin_nodes, support_nodes, edges, trail_edges, deviation_edges, loads
