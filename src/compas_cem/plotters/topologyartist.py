from math import copysign
from math import pi

import matplotlib.pyplot as plt

from compas.geometry import add_vectors
from compas.geometry import length_vector
from compas.geometry import scale_vector
from compas.geometry import translate_points
from compas.geometry import normalize_vector

from compas.geometry import Line
from compas.geometry import Rotation

# from compas_plotters import NetworkPlotter
from compas_plotters.artists import NetworkArtist

from compas_cem import COLORS


__all__ = ["TopologyArtist"]


class TopologyArtist(NetworkArtist):
    """
    An artists that draws a topology diagram.

    Parameters
    ----------
    topology_diagram : :class:`compas_cem.diagrams.TopologyDiagram`
        The topology diagram to plot.
    """
    def __init__(self,
                 topology_diagram,
                 nodetext=None,  # must be a dict, or 'key', or 'index'
                 edgetext=None,  # must be a dict, or 'key', or 'index'
                 nodes_load=None,
                 show_loads=True,
                 show_nodetext=False,
                 show_edgetext=False,
                 **kwargs):
        super(TopologyArtist, self).__init__(topology_diagram, **kwargs)

        self._node_colors = {"support": COLORS["node_support"],
                             "_origin": COLORS["node_origin"],
                             "default": COLORS["node"]}

        self._edge_state_colors = {-1.0: COLORS["compression"],
                                   1.0: COLORS["tension"],
                                   0.0: COLORS["edge"],
                                   "auxiliary_trail": COLORS["auxiliary_trail"]}

        self._edge_linestyles = {"trail": "-",  # solid
                                 "deviation": "--"}  # dashed

        self._topology = self.network
        self.datastructure = self.network

        self._float_precision = "3f"
        self.nodes_load = nodes_load
        self.show_loads = show_loads

        self.edge_text = edgetext
        self.node_text = nodetext
        self.show_nodetext = show_nodetext
        self.show_edgetext = show_edgetext

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

        super(TopologyArtist, self).draw_nodes(color=nc, *args, **kwargs)

    def draw_loads(self, nodes_load=None):
        """
        Draws the node loads as crosses inscribed in a circle.

        Parameters
        ----------
        nodes_load : ``list``
            The list of node identifiers where to draw the applied loads.
            Defaults to ``None``, wherein all nodes in will be considered.
        """
        topology = self.network
        flips = (-1, 1)
        angle = pi / 4.0  # rotate 45 degrees
        axis = [0.0, 0.0, 1.0]

        if not nodes_load:
            nodes_load = list(topology.loaded_nodes())

        self.nodes_load = nodes_load

        for node in self.nodes_load:

            xyz = topology.node_coordinates(node)
            nodesize = self.node_size[node]

            for f in flips:

                line = Line(*[add_vectors(xyz, [nodesize * f, 0.0, 0.0]) for f in flips])
                R = Rotation.from_axis_and_angle(axis=axis, angle=f*angle, point=xyz)
                line.transform(R)

                self.plotter.add(line,
                                 draw_as_segment=True,
                                 zorder=4000,
                                 linewidth=0.3)  # hardcoded, following value from COMPAS

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

            # draw auxiliary trail edges
            if edge in aux_keys:
                ec[edge] = cmap["auxiliary_trail"]
                continue
            # draw trail edges
            if ds.is_trail_edge(edge):
                attr_name = "length"
            # draw deviation edges
            else:
                attr_name = "force"
            ec[edge] = cmap[copysign(1.0, ds.edge_attribute(edge, attr_name))]

        super(TopologyArtist, self).draw_edges(color=ec, *args, **kwargs)
        edges = self._edgecollection
        lsmap = self.edge_linestyles
        els = [lsmap[ds.edge_attribute(e, "type")] for e in keys]
        edges.set_linestyle(els)

    def draw(self):
        """
        Draw nodes, edges, loads and labels.
        """
        self.clear()

        if self.show_nodes:
            self.draw_nodes()
        if self.show_edges:
            self.draw_edges()
        if self.show_loads:
            self.draw_loads()
        if self.show_nodetext:
            self.draw_nodelabels()
        if self.show_edgetext:
            self.draw_edgelabels()


    # def _draw_load_arrows(self, keys=None, scale=1.0, width=1.0, gap=0.05, tol=1e-3):
    #     """
    #     Draws the node loads in a ``TopologyDiagram`` as scaled arrows.

    #     Parameters
    #     ----------
    #     keys : ``list``
    #         The list of node keys where to draw forces.
    #         If nodes is ``None``, all nodes in will be considered.
    #         Defaults to ``None``.
    #     scale : ``float``
    #         The scale of the load arrows. Defaults to ``1.0``.
    #     width : ``float``
    #         The arrows uniform display width. Defaults to ``1.0``.
    #     gap : ``float``
    #         The offset between the node and the load. Defaults to ``0.2``.
    #     tol : ``float``
    #         The minimum force magnitude to draw. Defaults to ``1e-3``.
    #     """
    #     keys = keys or list(self.datastructure.nodes())
    #     attrs = ["qx", "qy", "qz"]
    #     color = COLORS["load"]
    #     shift = {key: False for key in keys}
    #     self._draw_forces(keys, attrs, scale, color, width, shift, gap, tol)


    # def save(self, filepath, tight=True, autoscale=True, bbox_inches="tight", pad_inches=0.0, **kwargs):
    #     """
    #     Saves the plot to a file.

    #     Parameters
    #     ----------
    #     filepath : str
    #         Full path of the file.
    #     """
    #     if autoscale:
    #         self.axes.autoscale(tight=False)

    #     if tight:
    #         plt.tight_layout()
    #         kwargs_tight = {"bbox_inches": bbox_inches, "pad_inches": pad_inches}
    #         kwargs.update(kwargs_tight)

    #     plt.savefig(filepath, **kwargs)

    # def _draw_forces(self, keys, attrs, scale, color, width, shift, gap, tol):
    #     """
    #     Base method to draw forces (residuals or loads) as scaled arrows.

    #     Parameters
    #     ----------
    #     keys : ``list``
    #         The list of node keys where to draw forces.
    #     attrs : ``list``
    #         The attribute names of the force vector to draw.
    #     scale : ``float``
    #         The forces scale factor.
    #     color : ``tuple``
    #         The forces' color in rgb.
    #     width : ``float``
    #         The forces  display width.
    #     shift : ``bool``
    #         A flat to shift an arrow one length along its own axis.
    #     gap : ``float``
    #         The offset between the node and the force.
    #     tol : ``float``
    #         The minimum force magnitude to draw.
    #     """
    #     ds = self.datastructure
    #     arrows = []

    #     for node in keys:
    #         q_vec = ds.node_attributes(node, attrs)
    #         q_vec_scaled = scale_vector(q_vec, scale)
    #         q_vec_norm = normalize_vector(q_vec)
    #         q_len = length_vector(q_vec)

    #         if q_len < tol:
    #             continue

    #         arrow = {}
    #         start = ds.node_xyz(node)
    #         end = add_vectors(start, q_vec_scaled)

    #         # shift
    #         gap_arrow = gap
    #         if shift[node]:
    #             gap_arrow = (gap + length_vector(q_vec_scaled)) * -1

    #         gap_vector = scale_vector(q_vec_norm, gap_arrow)
    #         start, end = translate_points([start, end], gap_vector)

    #         # create gap
    #         arrow["start"] = start
    #         arrow["end"] = end
    #         arrow["color"] = color
    #         arrow["width"] = width

    #         arrows.append(arrow)

    #     super(TopologyArtist, self).draw_arrows(arrows)


if __name__ == "__main__":
    pass
