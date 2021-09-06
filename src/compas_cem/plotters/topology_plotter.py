from math import copysign
from math import pi

import matplotlib.pyplot as plt

from compas.geometry import add_vectors
from compas.geometry import rotate_points_xy
from compas.geometry import length_vector
from compas.geometry import scale_vector
from compas.geometry import translate_points
from compas.geometry import normalize_vector

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
                                   0.0: COLORS["edge"],
                                   "auxiliary_trail": COLORS["auxiliary_trail"]}

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
        aux_keys = [tuple(aux_edge) for aux_edge in ds.auxiliary_trails()]

        ec = {}
        for edge in keys:
            if edge in aux_keys:
                ec[edge] = cmap["auxiliary_trail"]
                continue

            if ds.is_trail_edge(edge):
                attr_name = "length"
            else:
                attr_name = "force"
            ec[edge] = cmap[copysign(1.0, ds.edge_attribute(edge, attr_name))]

        edges = super(TopologyPlotter, self).draw_edges(color=ec, *args, **kwargs)

        lsmap = self.edge_linestyles
        els = [lsmap[ds.edge_attribute(e, "type")] for e in keys]
        edges.set_linestyle(els)

        return ec

    def draw_loads(self, keys=None, radius=0.1, width=0.5, draw_arrows=False, **kwargs):
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
        draw_arrows : ``bool``
            A flag to draw the loads as arrows. Defaults to ``False``.
        kwargs : ``dict``
            The named attributes to display the the arrows. Defaults to ``None``.
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

        if draw_arrows:
            self._draw_load_arrows(keys=keys, width=width, **kwargs)

        return lines

    def _draw_load_arrows(self, keys=None, scale=1.0, width=1.0, gap=0.05, tol=1e-3):
        """
        Draws the node loads in a ``TopologyDiagram`` as scaled arrows.

        Parameters
        ----------
        keys : ``list``
            The list of node keys where to draw forces.
            If nodes is ``None``, all nodes in will be considered.
            Defaults to ``None``.
        scale : ``float``
            The scale of the load arrows. Defaults to ``1.0``.
        width : ``float``
            The arrows uniform display width. Defaults to ``1.0``.
        gap : ``float``
            The offset between the node and the load. Defaults to ``0.2``.
        tol : ``float``
            The minimum force magnitude to draw. Defaults to ``1e-3``.
        """
        keys = keys or list(self.datastructure.nodes())
        attrs = ["qx", "qy", "qz"]
        color = COLORS["load"]
        shift = {key: False for key in keys}
        self._draw_forces(keys, attrs, scale, color, width, shift, gap, tol)

    def draw_segments(self, segments, color=(50, 50, 50), width=0.5, ls="--"):
        """
        Draws additional line segments on a ``TopologyDiagram``.

        Parameters
        ----------
        segments : ``list``
            The line segments as tuples of xyz coordinates.
        color : ``tuple``
            The lines uniform color in rgb. Defaults to gray, ``(40, 40, 40)``.
        width : ``float``
            The lines' uniform display width. Defaults to ``0.5``.
        """
        lines = []
        for segment in segments:
            line = {}
            start, end = segment

            line["start"] = start
            line["end"] = end
            line["color"] = color
            line["width"] = width

            lines.append(line)

        lines = super(TopologyPlotter, self).draw_lines(lines)
        lines.set_linestyle(ls)

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
            self.axes.autoscale(tight=False)

        if tight:
            plt.tight_layout()
            kwargs_tight = {"bbox_inches": bbox_inches, "pad_inches": pad_inches}
            kwargs.update(kwargs_tight)

        plt.savefig(filepath, **kwargs)

    def _draw_forces(self, keys, attrs, scale, color, width, shift, gap, tol):
        """
        Base method to draw forces (residuals or loads) as scaled arrows.

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
        shift : ``bool``
            A flat to shift an arrow one length along its own axis.
        gap : ``float``
            The offset between the node and the force.
        tol : ``float``
            The minimum force magnitude to draw.
        """
        ds = self.datastructure
        arrows = []

        for node in keys:
            q_vec = ds.node_attributes(node, attrs)
            q_vec_scaled = scale_vector(q_vec, scale)
            q_vec_norm = normalize_vector(q_vec)
            q_len = length_vector(q_vec)

            if q_len < tol:
                continue

            arrow = {}
            start = ds.node_xyz(node)
            end = add_vectors(start, q_vec_scaled)

            # shift
            gap_arrow = gap
            if shift[node]:
                gap_arrow = (gap + length_vector(q_vec_scaled)) * -1

            gap_vector = scale_vector(q_vec_norm, gap_arrow)
            start, end = translate_points([start, end], gap_vector)

            # create gap
            arrow["start"] = start
            arrow["end"] = end
            arrow["color"] = color
            arrow["width"] = width

            arrows.append(arrow)

        super(TopologyPlotter, self).draw_arrows(arrows)


if __name__ == "__main__":
    pass
