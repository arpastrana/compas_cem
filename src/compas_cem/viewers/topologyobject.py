from compas.colors import Color

from compas_cem import COLORS

from compas_cem.viewers import DiagramObject


__all__ = ["TopologyDiagramObject"]


class TopologyDiagramObject(DiagramObject):
    """
    An object to display a topology diagram.

    Parameters
    ----------
    form_diagram : :class:`~compas_cem.diagrams.TopologyDiagram`
        The form diagram to plot.
    """
    edgecolor_trail = Color.from_rgb255(*COLORS["trail"]).rgb
    edgecolor_deviation = Color.from_rgb255(*COLORS["edge_deviation"]).rgb
    edgecolor_auxiliary = Color.from_rgb255(*COLORS["auxiliary_trail"]).rgb
    origin_nodecolor = Color.from_rgb255(*COLORS["node_origin"]).rgb

    def __init__(self, topology_diagram, **kwargs):
        super(TopologyDiagramObject, self).__init__(topology_diagram, **kwargs)

        # COMPAS View2 requirement
        self.linecolors = self.edge_color
        self.pointcolors = self.node_color

    @property
    def edge_color(self):
        if not self._edge_color:
            edge_color = {}

            for edge in self.edges:
                # draw auxiliary trail edges
                if self.diagram.is_auxiliary_trail_edge(edge):
                    color = self.edgecolor_trail
                else:
                    # draw trail edges
                    if self.diagram.is_trail_edge(edge):
                        color = self.edgecolor_trail
                        # draw deviation edges
                    elif self.diagram.is_deviation_edge(edge):
                        color = self.edgecolor_deviation
                edge_color[edge] = color

            self._edge_color = edge_color

        return self._edge_color

    @property
    def node_color(self):
        if not self._node_color:
            node_color = {}
            for node in self.nodes:
                if self.diagram.is_node_support(node):
                    color = self.support_nodecolor
                elif self.diagram.is_node_origin(node):
                    color = self.origin_nodecolor
                else:
                    color = self.default_nodecolor
                node_color[node] = color
            self._node_color = node_color
        return self._node_color


if __name__ == "__main__":
    pass
