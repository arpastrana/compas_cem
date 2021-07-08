"""
Get the artists color scheme for the objects of the CEM framework.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem import COLORS
import rhinoscriptsyntax as rs


class ArtistColorsComponent(component):
    def RunScript(self):
        colors = {key: rs.CreateColor(c) for key, c in COLORS.items()}

        color_tension = colors["tension"]
        color_compression = colors["compression"]
        color_edge = colors["edge"]
        color_node = colors["node"]
        color_node_support = colors["node_support"]
        color_node_origin = colors["node_origin"]
        color_load = colors["load"]
        color_reaction = colors["support_force"]
        color_trail = colors["trail"]
        color_auxiliary_trail = colors["auxiliary_trail"]

        colors = (color_tension, color_compression, color_edge, color_node, color_node_support, color_node_origin, color_load, color_reaction, color_trail, color_auxiliary_trail)

        return colors
