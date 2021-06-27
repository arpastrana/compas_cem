from math import copysign

from compas.geometry import add_vectors
from compas.geometry import length_vector
from compas.geometry import scale_vector

from compas.utilities import geometric_key
from compas_plotters import NetworkPlotter

from compas_cem import COLORS


__all__ = ["TopologyPlotter"]


class TopologyPlotter (NetworkPlotter):
    """
    A plotter tailored to draw topology matters.

    Parameters
    ----------
    topology_diagram : :class:`compas_cem.diagrams.TopologyDiagram`
        The topology diagram to plot.
    """
    def __init__(self, topology_diagram, *args, **kwargs):
        super(TopologyPlotter, self).__init__(topology_diagram, *args, **kwargs)

        self._node_colors = {"support": COLORS["node_support"],
                             "root": COLORS["node_origin"],
                             "default": COLORS["node"]}

        self._edge_state_colors = {-1: COLORS["compression"],
                                   1: COLORS["tension"],
                                   0: COLORS["edge"]}

        self._edge_linestyles = {"trail": "-",  # solid
                                 "deviation": "--"}  # dashed

        self._topology = self.datastructure
        self._float_precision = "3f"

    @property
    def topology(self):
        """
        The topology diagram to plot.

        Returns
        -------
        topology : :class:`compas_cem.diagrams.TopologyDiagram`
            A topology diagram.
        """
        return self._topology

    @property
    def node_colors(self):
        """
        The colors to draw the nodes of a topology diagram.

        Returns
        -------
        node_colors : ``dict`` of ``color``
            A dictionary that maps node type to RGB color.
        """
        return self._node_colors

    @property
    def edge_state_colors(self):
        """
        The colors to draw edges based on the forces acting on them.

        Returns
        -------
        edge_state_colors : ``dict`` of ``color``
            A dictionary that maps edge force to RGB color.
        """
        return self._edge_state_colors

    @property
    def edge_linestyles(self):
        """
        The linestyles used to draw edges based on the their topological type.

        Returns
        -------
        edge_linestyles: ``dict`` of ``str``
            A dictionary that maps edge type to linestyle.
        """
        return self._edge_linestyles

    @property
    def float_precision(self):
        """
        The default decimal precision to render float values as text.

        Returns
        -------
        precision: ``str``
            The float precision value. Defaults to ``3f``.
        """
        return self._float_precision

    def draw_nodes(self, *args, **kwargs):
        """
        Draws the nodes of a ``TopologyDiagram``.

        Parameters
        ----------
        keys : ``list`` of ``int``
            The keys of the nodes to plot.
        radius : ``float``, ``dict`` of ``float``
            The radius of the nodes.
        text : ``str``, ``dict`` of ``str``
            A dictionary of strings to render on the nodes.
        facecolor : ``color``, ``dict`` of ``color``
            Color for the node circle fill in (r, g, b) format.
        edgecolor : ``color``, ``dict`` of ``color``
            Color for the node circle edge in (r, g, b) format.
        edgewidth : ``float``, ``dict`` of ``float``
            Width for the node circle edge.
        textcolor : ``color``, ``dict`` of ``color``
            Color for the text to be displayed on the nodes.
        fontsize : ``int``, ``dict`` of ``int``
            Font size for the text to be displayed on the nodes.

        Returns
        -------
        collection : ``matplotlib.collection``
            A matplotlib point collection object.

        Notes
        -----
        When the parameters are passed as single value, this will be applied to
        all the nodes or edges in the ``TopologyDiagram``.
        If instead, a dictionary that maps ``{node_key: attribute}`` is given,
        specific values can be assigned individually.
        """
        cmap = self.node_colors
        ds = self.datastructure
        cmap["d"] = (255, 255, 255)  # default color
        nc = {n: cmap[ds.node_attribute(n, "type") or "d"] for n in ds.nodes()}

        super(TopologyPlotter, self).draw_nodes(facecolor=nc, *args, **kwargs)

    def draw_edges(self, keys=None, *args, **kwargs):
        """
        Draws the edges of a ``TopologyDiagram``.

        Parameters
        ----------
        keys : ``list`` of ``tuple``
            The keys of the edges to plot.
            Defaults to ``None``.
        width : ``float``, ``dict`` of ``float``
            Width of the edges.
        color : ``color``, ``dict`` of ``color``
            Color of the edges in (r, g, b) format.
        text : ``str``, ``dict`` of ``str``
            A dictionary of strings to render on the nodes.
        textcolor : ``color``, ``dict`` of ``color``
            Color for the text to be displayed on the nodes.
        fontsize : ``int``, ``dict`` of ``int``
            Font size for the text to be displayed on the nodes.

        Returns
        -------
        collection : ``matplotlib.collection``
            A matplotlib point collection object.

        Notes
        -----
        When the parameters are passed as single value, this will be applied to
        all the nodes or edges in the ``TopologyDiagram``.
        If instead, a dictionary that maps ``{edge_key: attribute}`` is given,
        specific values can be assigned individually.
        """
        ds = self.datastructure

        if keys is None:
            keys = list(ds.edges())

        cmap = self.edge_state_colors
        ec = {e: cmap[copysign(1.0, ds.edge_attribute(e, "force") or 0.0)] for e in keys}

        edges = super(TopologyPlotter, self).draw_edges(keys=keys, color=ec, *args, **kwargs)

        lsmap = self.edge_linestyles
        els = [lsmap[ds.edge_attribute(e, "type")] for e in keys]
        edges.set_linestyle(els)

        return edges

    def draw_loads(self, keys=None, scale=1.0, width=1.0, tol=1e-3):
        """
        Draws the node loads in a ``FormDiagram`` as scaled arrows.

        Parameters
        ----------
        keys : ``list``
            The list of node keys where to draw forces.
            If nodes is ``None``, all nodes in will be considered.
            Defaults to ``None``.
        scale : ``float``
            The scale of the load arrows. Defaults to ``1.0``.
        width : ``float``
            The arrows uniform display width. Defaults to ``4.0``.
        tol : ``float``
            The minimum force magnitude to draw. Defaults to ``1e-3``.
        """
        if not keys:
            keys = list(self.datastructure.nodes())
        attrs = ["qx", "qy", "qz"]
        color = COLORS["load"]
        self._draw_forces(keys, attrs, scale, color, width, tol)

    def draw_residuals(self, keys=None, scale=1.0, width=1.0, tol=1e-3):
        """
        Draws the node residual forces in a ``FormDiagram`` as scaled arrows.

        Parameters
        ----------
        keys : ``list``
            The list of node keys where to draw forces.
            If nodes is ``None``, all nodes in will be considered.
            Defaults to ``None``.
        scale : ``float``
            The scale of the residual arrows. Defaults to ``1.0``.
        width : ``float``
            The arrows uniform display width. Defaults to ``3.0``.
        tol : ``float``
            The minimum force magnitude to draw. Defaults to ``1e-3``.
        """
        if not keys:
            keys = list(self.datastructure.nodes())
        attrs = ["rx", "ry", "rz"]
        color = COLORS["support_force"]
        self._draw_forces(keys, attrs, scale, color, width, tol)

    def _draw_forces(self, keys, attrs, scale, color, width, tol):
        """
        Base method to draws forces (residuals or loads) as scaled arrows.

        Parameters
        ----------
        keys : ``list``
            The list of node keys where to draw forces.
        attrs : ``list``
            The attribute names of the force vector to draw.
        scale : ``float``
            The forces scale factor.
        color : ``tuple``
            The forces' color in rgb.
        width : ``float``
            The forces  display width.
        tol : ``float``
            The minimum force magnitude to draw.
        """
        ds = self.datastructure
        arrows = []

        for node in ds.nodes():
            q_vec = ds.node_attributes(node, attrs)

            if length_vector(q_vec) < tol:
                continue

            arrow = {}
            arrow["start"] = ds.node_xyz(node)
            pt = scale_vector(q_vec, -scale)
            arrow["end"] = add_vectors(arrow["start"], pt)
            arrow["color"] = color
            arrow["width"] = width

            arrows.append(arrow)

        super(TopologyPlotter, self).draw_arrows(arrows)


if __name__ == "__main__":
    pass
