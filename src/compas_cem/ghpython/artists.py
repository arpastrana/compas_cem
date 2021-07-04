from compas_ghpython.artists import NetworkArtist
from compas_ghpython import draw_points

from compas_cem import COLORS


__all__ = ["FormArtist", "TopologyArtist"]


class FormArtist(NetworkArtist):
    """
    """
    def __init__(self, form_diagram, *args, **kwargs):
        super(FormArtist, self).__init__(form_diagram, *args, **kwargs)

        self.edge_colors = {"trail": COLORS["edge"],
                            "deviation": COLORS["edge"]}

        self.edge_state_colors = {-1: COLORS["compression"],
                                  1: COLORS["tension"],
                                  0: COLORS["edge"]}

        self.float_precision = "3f"
        self._form = form_diagram

    @property
    def form(self):
        """
        The form diagram to draw.

        Returns
        -------
        form : :class:`compas_cem.diagrams.FormDiagram`
            A form diagram.
        """
        return self._form

    @form.setter
    def form(self, form):
        self._form = form

    def draw_nodes(self, nodes=None, color=None):
        """Draw a selection of nodes.
        Parameters
        ----------
        nodes: list, optional
            The selection of nodes that should be drawn.
            Default is ``None``, in which case all nodes are drawn.

        Returns
        -------
        list of :class:`Rhino.Geometry.Point3d`
        """
        nodes = nodes or list(self.form.nodes())
        points = []
        for node in nodes:
            points.append({'pos': self.form.node_coordinates(node)})

        return draw_points(points)


class TopologyArtist(NetworkArtist):
    pass
