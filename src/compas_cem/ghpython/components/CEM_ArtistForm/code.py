"""
Draw a form diagram.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas.artists import Artist


class FormArtistComponent(component):
    def RunScript(self, form, node_keys, edge_keys, force_min, force_scale):
        node_keys = node_keys or None
        edge_keys = edge_keys or None
        force_min = force_min or 1e-3
        force_scale = force_scale or 1

        if not form:
            return

        artist = Artist(form)

        nodes = artist.draw_nodes(node_keys)
        edges = artist.draw_edges(edge_keys)
        support_nodes = artist.draw_nodes_support(node_keys)

        loads = artist.draw_loads(node_keys, min_load=force_min, scale=force_scale)
        reactions = artist.draw_reactions(node_keys, min_force=force_min, scale=force_scale)

        return nodes, support_nodes, edges, loads, reactions
