"""
Draw a topology diagram.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas.artists import Artist


class TopologyArtistComponent(component):
    def RunScript(self, topology, node_keys, edge_keys, force_min, force_scale):
        node_keys = node_keys or None
        edge_keys = edge_keys or None
        force_min = force_min or 1e-3
        force_scale = force_scale or 1.0

        if not topology:
            return

        artist = Artist(topology)

        nodes = artist.draw_nodes(node_keys)
        origin_nodes = artist.draw_nodes_origin(node_keys)
        support_nodes = artist.draw_nodes_support(node_keys)

        edges = artist.draw_edges(edge_keys)
        trail_edges = artist.draw_edges_trail(edge_keys)
        deviation_edges = artist.draw_edges_deviation(edge_keys)

        trails = artist.draw_trails()

        loads = artist.draw_loads(node_keys, min_load=force_min, scale=force_scale)

        return nodes, origin_nodes, support_nodes, edges, trail_edges, deviation_edges, trails, loads
