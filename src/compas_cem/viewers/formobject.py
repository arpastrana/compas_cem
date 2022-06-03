from compas.colors import Color

from compas_cem import COLORS

from compas_cem.viewers import DiagramObject


__all__ = ["FormDiagramObject"]


class FormDiagramObject(DiagramObject):
    """
    An object to display a form diagram.

    Parameters
    ----------
    form_diagram : :class:`~compas_cem.diagrams.FormDiagram`
        The form diagram to plot.
    """
    edgecolor_tension = Color.from_rgb255(*COLORS["tension"]).rgb
    edgecolor_compression = Color.from_rgb255(*COLORS["compression"]).rgb

    def __init__(self, form_diagram, **kwargs):
        super(FormDiagramObject, self).__init__(form_diagram, **kwargs)

        # COMPAS View2 requirement
        self.linecolors = self.edge_color
        self.pointcolors = self.node_color

    @property
    def edge_color(self):
        if not self._edge_color:
            edge_color = {}
            for edge in self.edges:
                edge_force = self.diagram.edge_force(edge)
                if edge_force >= 0.0:
                    color = self.edgecolor_tension
                elif edge_force < 0.0:
                    color = self.edgecolor_compression
                else:
                    color = self.default_edgecolor
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
                else:
                    color = self.default_nodecolor
                node_color[node] = color
            self._node_color = node_color
        return self._node_color


if __name__ == "__main__":
    pass
