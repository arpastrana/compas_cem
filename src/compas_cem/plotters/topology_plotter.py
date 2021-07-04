from math import copysign
from math import pi

import matplotlib.pyplot as plt

from compas.geometry import add_vectors
from compas.geometry import rotate_points_xy

from compas_plotters import NetworkPlotter

from compas_cem import COLORS


__all__ = ["TopologyPlotter"]


class TopologyPlotter(NetworkPlotter):
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
                             "_origin": COLORS["node_origin"],
                             "default": COLORS["node"]}

        self._edge_state_colors = {-1.0: COLORS["compression"],
                                   1.0: COLORS["tension"],
                                   0.0: COLORS["edge"]}

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

    def draw_edges(self, *args, **kwargs):
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
        cmap = self.edge_state_colors

        keys = list(ds.edges())

        ec = {}
        for edge in keys:
            if ds.is_trail_edge(edge):
                attr_name = "length"
            else:
                attr_name = "force"
            ec[edge] = cmap[copysign(1.0, ds.edge_attribute(edge, attr_name))]

        edges = super(TopologyPlotter, self).draw_edges(color=ec, *args, **kwargs)

        lsmap = self.edge_linestyles
        els = [lsmap[ds.edge_attribute(e, "type")] for e in keys]
        edges.set_linestyle(els)

        return keys

    def draw_loads(self, keys=None, radius=0.1, width=0.5):
        """
        Draws the node loads as crosses inscribed in a circle.

        Parameters
        ----------
        keys : ``list``
            The list of node keys where to draw forces.
            If nodes is ``None``, all nodes in will be considered.
            Defaults to ``None``.
        radius : ``float``, ``dict`` of ``float``
            The radius of the loads. Defaults to ``0.1``.
        width : ``float``
            The arrows uniform display width. Defaults to ``0.5``.
        """
        topology = self.datastructure
        flips = (-1, 1)
        angle = pi / 4.0

        if not keys:
            keys = list(topology.nodes())

        loads = []
        for node in keys:
            if not topology.is_node_loaded(node):
                continue

            xyz = topology.node_coordinates(node)
            line = [add_vectors(xyz, [radius * f, 0.0, 0.0]) for f in flips]

            for f in flips:
                start, end = rotate_points_xy(line, angle=f*angle, origin=xyz)

                load = {}
                load['start'] = start
                load['end'] = end
                load['color'] = (0, 0, 0)  # black
                load['width'] = width

                loads.append(load)

        lines = self.draw_lines(loads)
        lines.set_zorder(4000)

        return lines

    def save(self, filepath, tight=True, autoscale=True, bbox_inches="tight", pad_inches=0.0, **kwargs):
        """
        Saves the plot to a file.

        Parameters
        ----------
        filepath : str
            Full path of the file.
        """
        if autoscale:
            self.axes.autoscale(tight=tight)

        if tight:
            plt.tight_layout()
            kwargs_tight = {"bbox_inches": bbox_inches, "pad_inches": pad_inches}
            kwargs.update(kwargs_tight)

        plt.savefig(filepath, **kwargs)


if __name__ == "__main__":
    pass
