from math import copysign
from math import pi
from math import fabs

from compas_cem import COLORS

from compas.geometry import add_vectors
from compas.geometry import Line
from compas.geometry import Rotation
from compas.utilities import geometric_key

from compas_plotters.artists import NetworkArtist


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

        self.node_colors = {"support": COLORS["node_support"],
                            "_origin": COLORS["node_origin"],
                            "default": COLORS["node"]}

        self.edge_statecolors = {-1.0: COLORS["compression"],
                                 1.0: COLORS["tension"],
                                 0.0: COLORS["edge"],
                                 "auxiliary_trail": COLORS["auxiliary_trail"]}

        self.edge_linestyles = {"trail": "-",  # solid
                                "deviation": "--"}  # dashed

        self.float_precision = "2f"

        self.topology = self.network

        self.edge_text = self._edge_textlabel(edgetext)
        self.node_text = self._node_textlabel(nodetext)

        self.show_loads = show_loads
        self.show_nodetext = show_nodetext
        self.show_edgetext = show_edgetext

    def draw_nodes(self):
        """
        Draw the nodes of a topology diagram.
        """
        cmap = self.node_colors
        node_color = {}
        for node in self.topology.nodes():
            key = self.topology.node_attribute(node, "type") or "default"
            node_color[node] = cmap[key]

        super(TopologyArtist, self).draw_nodes(color=node_color)

    def draw_loads(self):
        """
        Draw the node loads as crosses inscribed in a circle.
        """
        flips = (-1, 1)
        angle = pi / 4.0  # rotate 45 degrees
        axis = [0.0, 0.0, 1.0]

        for node in self.topology.loaded_nodes():

            if node not in self.nodes:
                continue

            xyz = self.topology.node_coordinates(node)
            nodesize = self.node_size[node]

            for f in flips:

                line = Line(*[add_vectors(xyz, [nodesize * f, 0.0, 0.0]) for f in flips])
                R = Rotation.from_axis_and_angle(axis=axis, angle=f*angle, point=xyz)
                line.transform(R)

                self.plotter.add(line,
                                 draw_as_segment=True,
                                 zorder=4000,
                                 linewidth=0.3)  # hardcoded, following value from COMPAS

    def draw_edges(self):
        """
        Draw the edges of a topology diagram.
        """
        topology = self.topology
        cmap = self.edge_statecolors

        edges = list(topology.edges())
        edge_color = {}
        for edge in edges:
            # draw auxiliary trail edges
            if topology.is_auxiliary_trail_edge(edge):
                edge_color[edge] = cmap["auxiliary_trail"]
            else:
                # draw trail edges
                if topology.is_trail_edge(edge):
                    attr_name = "length"
                    # draw deviation edges
                elif topology.is_deviation_edge(edge):
                    attr_name = "force"

                ckey = copysign(1.0, topology.edge_attribute(edge, attr_name))
                edge_color[edge] = cmap[ckey]

        # draw edges
        super(TopologyArtist, self).draw_edges(color=edge_color)

        # change linestyle
        edge_lines = self._edgecollection
        lsmap = self.edge_linestyles
        els = [lsmap[topology.edge_attribute(e, "type")] for e in edges]
        edge_lines.set_linestyle(els)

    def draw(self):
        """
        Draw the nodes, the edges, the loads and the labels of a topology diagram.
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

    def _node_textlabel(self, text_tag):
        """
        Generate text labels to plot on the nodes of a topology diagram.

        Input
        -----
        text_tag : `str`
            Tag query. Supported tags are: "xyz", "keyxyz" and "type".

        Returns
        -------
        text_labels : ``dict``
            A dictionary of text labels
        """
        def gkey_format(x):
            return geometric_key(self.topology.node_xyz(x), precision)

        def key_gkey_format(x):
            return "{}\n{}".format(x, gkey_format(x))

        def type_format(x):
            return "{}".format(self.topology.node_attribute(x, "type"))

        precision = self.float_precision

        tags_formatter = {"xyz": gkey_format,
                          "keyxyz": key_gkey_format,
                          "type": type_format}

        if text_tag not in tags_formatter:
            return None

        text_labels = {}
        formatter = tags_formatter[text_tag]

        for node in self.topology.nodes():
            label = formatter(node)
            text_labels[node] = label

        return text_labels

    def _edge_textlabel(self, text_tag):
        """
        Generate text labels to plot on the edges of a topology diagram.

        Input
        -----
        text_tag : `str`
            Tag query.
            Supported tags are: "force", "length", "state", "forcelengthstate" and "type".

        Returns
        -------
        text_labels : ``dict``
            A dictionary of text labels
        """
        def force_format(x):
            return "{0:.{1}}".format(fabs(self.topology.edge_force(x)), precision)

        def length_format(x):
            return "{0:.{1}}".format(fabs(self.topology.edge_length_2(x)), precision)

        def force_length_format(x):
            return "f: {}\nl: {}".format(force_format(x), length_format(x))

        def state_format(x):
            if self.topology.is_trail_edge(x):
                parameter = self.topology.edge_length_2(edge)
            else:
                parameter = self.topology.edge_force(edge)
            state = copysign(1.00, parameter)
            return "{0:.{1}}".format(state, precision)

        def type_format(x):
            return "{}".format(self.topology.edge_attribute(x, "type"))

        def force_length_state_format(x):
            return "f: {}\nl: {}\ns: {}".format(force_format(x), length_format(x), state_format(x))

        precision = self.float_precision

        tags_formatter = {"force": force_format,
                          "length": length_format,
                          "state": state_format,
                          "forcelengthstate": force_length_state_format,
                          "type": type_format}

        if text_tag not in tags_formatter:
            return None

        text_labels = {}
        formatter = tags_formatter[text_tag]

        for edge in self.topology.edges():
            label = formatter(edge)
            text_labels[edge] = label

        return text_labels


if __name__ == "__main__":
    pass
