"""
Draw a form diagram.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.ghpython import FormArtist


class FormArtistComponent(component):
    def RunScript(self, form, node, edge, force_min, force_scale):
        node = node or None
        edge = edge or None
        force_min = force_min or 1e-3
        force_scale = force_scale or 1
        if form:
            artist = FormArtist(form)

            nodes = artist.draw_nodes(node)
            edges = artist.draw_edges(edge)
            support_nodes = artist.draw_nodes_support(node)

            loads = artist.draw_loads(node, min_load=force_min, scale=force_scale)
            reactions = artist.draw_reactions(node, min_force=force_min, scale=force_scale)

            return nodes, support_nodes, edges, loads, reactions
