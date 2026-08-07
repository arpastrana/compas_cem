from math import copysign
from math import fabs
from math import pi

from compas.colors import Color
from compas.colors import ColorMap
from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Rotation
from compas.geometry import Vector
from compas.geometry import add_vectors
from compas.geometry import length_vector
from compas.geometry import normalize_vector
from compas.geometry import scale_vector
from compas.geometry import translate_points
from compas.scene import register
from compas.tolerance import TOL
from compas_plotter.scene import GraphObject
from compas_plotter.scene.plotterobject import to_rgb
from matplotlib.collections import LineCollection

from compas_cem import COLORS
from compas_cem.diagrams import FormDiagram
from compas_cem.diagrams import TopologyDiagram

__all__ = [
    "DiagramPlotterObject",
    "FormPlotterObject",
    "TopologyPlotterObject",
    "register_plotter_scene_objects",
]


def _color(name):
    """
    Look a package color up as a COMPAS color.
    """
    return Color.from_rgb255(*COLORS[name])


class DiagramPlotterObject(GraphObject):
    """
    A scene object that draws a diagram in a plotter.

    Parameters
    ----------
    nodesize :
        The radius of the node markers.
    edgewidth :
        The width of the edges. A pair is read as the bounds to spread the
        edge forces over.
    nodetext :
        A tag naming what to label the nodes with, or a mapping of nodes to
        labels.
    edgetext :
        A tag naming what to label the edges with, or a mapping of edges to
        labels.
    show_nodetext :
        Whether to draw the node labels.
    show_edgetext :
        Whether to draw the edge labels.
    sizepolicy :
        If `relative`, the node size is divided by the number of nodes. If
        `absolute`, it is divided by the resolution of the plotter.

    Notes
    -----
    The size policy defaults to `relative`, which is what the diagram artists
    of the 1.x plotter used. The upstream scene object defaults to `absolute`
    instead, which makes the same node size read two orders of magnitude
    smaller.
    """

    def __init__(
        self,
        nodesize=0.1,
        edgewidth=1.0,
        nodetext=None,
        edgetext=None,
        show_nodetext=False,
        show_edgetext=False,
        sizepolicy="relative",
        **kwargs,
    ):
        super(DiagramPlotterObject, self).__init__(
            nodesize=nodesize,
            edgewidth=edgewidth,
            sizepolicy=sizepolicy,
            **kwargs,
        )

        self.float_precision = "2f"

        self.show_nodetext = show_nodetext
        self.show_edgetext = show_edgetext

        self._nodetext_tag = nodetext
        self._edgetext_tag = edgetext

    # ==========================================================================
    # Diagram
    # ==========================================================================

    @property
    def diagram(self):
        """
        The diagram this object draws.
        """
        return self.graph

    # ==========================================================================
    # Style
    # ==========================================================================

    def resolve_style(self):
        """
        Derive the styling of the diagram from its current state.

        Notes
        -----
        The styling is resolved on every draw rather than at construction, so a
        redraw picks up changes made to the diagram in between.
        """
        raise NotImplementedError

    def edge_widths(self):
        """
        The width to draw every edge with.

        Returns
        -------
        widths :
            A mapping of edges to widths.

        Notes
        -----
        A single width is used for every edge unless a pair of bounds is given,
        in which case the absolute edge forces are spread linearly over them.
        """
        edgewidth = self.edgewidth

        if not isinstance(edgewidth, (tuple, list)):
            return {edge: edgewidth for edge in self.diagram.edges()}

        low, high = edgewidth
        forces = [fabs(self.diagram.edge_force(edge)) for edge in self.diagram.edges()]
        forcemin = min(forces)
        forcemax = max(forces)

        widths = {}
        for edge in self.diagram.edges():
            force = fabs(self.diagram.edge_force(edge))
            try:
                ratio = (force - forcemin) / (forcemax - forcemin)
            except ZeroDivisionError:
                ratio = 1.0
            widths[edge] = (1.0 - ratio) * low + ratio * high

        return widths

    def edge_linestyles(self):
        """
        The line style to draw every edge with.

        Returns
        -------
        linestyles :
            A mapping of edges to matplotlib line styles, or `None` to draw
            every edge solid.
        """
        return None

    # ==========================================================================
    # Draw
    # ==========================================================================

    def draw(self):
        """
        Draw the diagram, its forces and its labels.
        """
        self.resolve_style()

        if self.show_nodetext:
            labels = self.node_textlabels(self._nodetext_tag)
            self.nodetext = self.default_node_textlabels() if labels is None else labels
        else:
            self.nodetext = {}

        if self.show_edgetext:
            labels = self.edge_textlabels(self._edgetext_tag)
            self.edgetext = self.default_edge_textlabels() if labels is None else labels
        else:
            self.edgetext = {}

        super(DiagramPlotterObject, self).draw()

        self.draw_forces()

        return self._mpl_objects

    def draw_forces(self):
        """
        Draw the loads and the reaction forces of the diagram.
        """
        pass

    def _draw_edges(self, node_xyz):
        """
        Draw the edges with their own width and line style.

        Notes
        -----
        This replaces the upstream edge pass, which broadcasts one width and
        one line style across every edge.
        """
        edges = list(self.diagram.edges())

        lines = [[node_xyz[u][:2], node_xyz[v][:2]] for u, v in edges]
        colors = [to_rgb(self.edgecolor[edge]) for edge in edges]

        widths = self.edge_widths()
        widths = [widths[edge] for edge in edges]

        collection = LineCollection(
            lines,
            linewidths=widths,
            colors=colors,
            zorder=self.zorder + 10,
        )

        linestyles = self.edge_linestyles()
        if linestyles is not None:
            collection.set_linestyle([linestyles[edge] for edge in edges])

        self.axes.add_collection(collection)
        self._mpl_objects.append(collection)

    def _draw_arrows(self, nodes, attr_names, scale, color, shift, tol):
        """
        Draw forces at a set of nodes as scaled arrows.

        Parameters
        ----------
        nodes :
            The nodes to draw a force at.
        attr_names :
            The node attributes that hold the force vector.
        scale :
            The factor to scale the force vectors by.
        color :
            The color to draw the arrows in.
        shift :
            A mapping of nodes to whether the arrow is shifted one length along
            its own axis.
        tol :
            The smallest force magnitude worth drawing.
        """
        diagram = self.diagram
        radius = self._node_radius()

        for node in nodes:
            vector = diagram.node_attributes(node, attr_names)
            length = length_vector(vector)

            if length < tol:
                continue

            scaled = scale_vector(vector, scale)
            start = diagram.node_coordinates(node)
            end = add_vectors(start, scaled)

            gap = radius
            if shift[node]:
                gap = (gap + length_vector(scaled)) * -1

            gap_vector = scale_vector(normalize_vector(vector), gap)
            start, end = translate_points([start, end], gap_vector)

            start = Point(*start)
            force = Vector.from_start_end(start, end)

            self.plotter.add(force, point=start, color=color)

    # ==========================================================================
    # Labels
    # ==========================================================================

    def node_textlabels(self, tag):
        """
        Build the labels to draw on the nodes.

        Parameters
        ----------
        tag :
            A tag naming what to label the nodes with, or a mapping of nodes to
            labels, which is returned unchanged.

        Returns
        -------
        labels :
            A mapping of nodes to labels, or `None` if the tag is unsupported.
        """
        if tag is None or isinstance(tag, dict):
            return tag

        formatters = self.node_textlabel_formatters()
        if tag not in formatters:
            return None

        formatter = formatters[tag]

        return {node: formatter(node) for node in self.diagram.nodes()}

    def edge_textlabels(self, tag):
        """
        Build the labels to draw on the edges.

        Parameters
        ----------
        tag :
            A tag naming what to label the edges with, or a mapping of edges to
            labels, which is returned unchanged.

        Returns
        -------
        labels :
            A mapping of edges to labels, or `None` if the tag is unsupported.
        """
        if tag is None or isinstance(tag, dict):
            return tag

        formatters = self.edge_textlabel_formatters()
        if tag not in formatters:
            return None

        formatter = formatters[tag]

        return {edge: formatter(edge) for edge in self.diagram.edges()}

    def default_node_textlabels(self):
        """
        The node labels used when no tag names something else to show.
        """
        return {node: str(node) for node in self.diagram.nodes()}

    def default_edge_textlabels(self):
        """
        The edge labels used when no tag names something else to show.
        """
        return {(u, v): "{}-{}".format(u, v) for u, v in self.diagram.edges()}

    def node_textlabel_formatters(self):
        """
        The supported node label tags and the formatter of each.
        """
        precision = self.float_precision
        diagram = self.diagram

        def gkey_format(node):
            return TOL.geometric_key(diagram.node_coordinates(node), precision)

        def key_gkey_format(node):
            return "{}\n{}".format(node, gkey_format(node))

        return {"xyz": gkey_format, "keyxyz": key_gkey_format}

    def edge_textlabel_formatters(self):
        """
        The supported edge label tags and the formatter of each.
        """
        return {}


class FormPlotterObject(DiagramPlotterObject):
    """
    A scene object that draws a form diagram in a plotter.

    Parameters
    ----------
    loadtol :
        The smallest load magnitude worth drawing.
    loadscale :
        The factor to scale the load vectors by.
    reactiontol :
        The smallest reaction force magnitude worth drawing.
    reactionscale :
        The factor to scale the reaction force vectors by.
    show_loads :
        Whether to draw the loads.
    show_reactions :
        Whether to draw the reaction forces.
    """

    def __init__(
        self,
        loadtol=1e-3,
        loadscale=1.0,
        reactiontol=1e-3,
        reactionscale=1.0,
        show_loads=True,
        show_reactions=True,
        **kwargs,
    ):
        super(FormPlotterObject, self).__init__(**kwargs)

        self.edge_statecolors = {
            -1: _color("compression"),
            1: _color("tension"),
            0: _color("edge"),
        }

        self.node_colors = {
            "support": _color("node_support"),
            "default": _color("node"),
        }

        self.load_color = _color("load")
        self.load_attrs = ["qx", "qy", "qz"]
        self.load_tol = loadtol
        self.load_scale = loadscale

        self.reaction_color = _color("support_force")
        self.reaction_attrs = ["rx", "ry", "rz"]
        self.reaction_tol = reactiontol
        self.reaction_scale = reactionscale

        self.show_loads = show_loads
        self.show_reactions = show_reactions

    @property
    def form(self):
        """
        The form diagram this object draws.
        """
        return self.graph

    def resolve_style(self):
        """
        Color the nodes by support and the edges by their force state.
        """
        form = self.form
        cmap = self.node_colors

        self.nodecolor = {
            node: cmap["support"] if form.is_node_support(node) else cmap["default"]
            for node in form.nodes()
        }

        cmap = self.edge_statecolors
        edgecolor = {}
        for edge in form.edges():
            force = form.edge_force(edge)
            edgecolor[edge] = cmap[0] if force == 0.0 else cmap[copysign(1, force)]

        self.edgecolor = edgecolor

    def draw_forces(self):
        """
        Draw the loads and the reaction forces of the form diagram.
        """
        nodes = list(self.form.nodes())

        if self.show_loads:
            self._draw_arrows(
                nodes=nodes,
                attr_names=self.load_attrs,
                scale=self.load_scale,
                color=self.load_color,
                tol=self.load_tol,
                shift={node: False for node in nodes},
            )

        if self.show_reactions:
            self._draw_arrows(
                nodes=nodes,
                attr_names=self.reaction_attrs,
                scale=self.reaction_scale,
                color=self.reaction_color,
                tol=self.reaction_tol,
                shift=self._reaction_shifts(),
            )

    def _reaction_shifts(self):
        """
        Whether the reaction arrow at every node points back into its trail.

        Notes
        -----
        A reaction is shifted when the strongest edge meeting the node is in
        compression, so the arrow reads as pushing against the support rather
        than pulling away from it.

        TODO: needs a more robust check for arrow orientation. What is wanted
        is to know whether the arrow needs a full shift.
        """
        form = self.form
        shifts = {}

        for node in form.nodes():
            forces = [form.edge_force(e) for e in form.node_connected_edges(node)]
            if not forces:
                shifts[node] = False
                continue
            shifts[node] = max(forces, key=lambda f: fabs(f)) < 0.0

        return shifts

    def edge_textlabel_formatters(self):
        """
        The supported edge label tags and the formatter of each.
        """
        precision = self.float_precision
        form = self.form

        def force_format(edge):
            return "{0:.{1}}".format(form.edge_force(edge), precision)

        def length_format(edge):
            return "{0:.{1}}".format(form.edge_length(edge), precision)

        def force_length_format(edge):
            return "f: {}\nl: {}".format(force_format(edge), length_format(edge))

        return {
            "force": force_format,
            "length": length_format,
            "forcelength": force_length_format,
        }


class TopologyPlotterObject(DiagramPlotterObject):
    """
    A scene object that draws a topology diagram in a plotter.

    Parameters
    ----------
    nodecolor :
        What to color the nodes by, either `type` or `sequence`.
    edgecolor :
        What to color the edges by, either `state` or `type`.
    show_loads :
        Whether to draw the loads.
    """

    def __init__(
        self,
        nodecolor=None,
        edgecolor=None,
        show_loads=True,
        **kwargs,
    ):
        super(TopologyPlotterObject, self).__init__(**kwargs)

        self.node_typecolors = {
            "support": _color("node_support"),
            "_origin": _color("node_origin"),
            "default": _color("node"),
        }

        self.node_sequencecolors = ColorMap.from_color(_color("trail"), "light")

        self.edge_statecolors = {
            -1.0: _color("compression"),
            1.0: _color("tension"),
            0.0: _color("edge"),
            "auxiliary_trail": _color("auxiliary_trail"),
        }

        self.edge_typecolors = {name: _color(name) for name in COLORS}

        self.linestyles = {"trail": "-", "deviation": "--"}

        self.node_colors = nodecolor or "type"
        self.edge_colors = edgecolor or "state"

        self.show_loads = show_loads

    @property
    def topology(self):
        """
        The topology diagram this object draws.
        """
        return self.graph

    def resolve_style(self):
        """
        Color the nodes and the edges by the chosen attribute.
        """
        self.nodecolor = self._node_colors()
        self.edgecolor = self._edge_colors()

    def _node_colors(self):
        """
        The color of every node, by node type or by trail sequence.
        """
        topology = self.topology

        if self.node_colors == "sequence":
            maxval = topology.sequence_last()
            return {
                node: self.node_sequencecolors(
                    float(topology.node_attribute(node, "_k")), maxval=maxval
                )
                for node in topology.nodes()
            }

        cmap = self.node_typecolors

        return {
            node: cmap[topology.node_attribute(node, "type") or "default"]
            for node in topology.nodes()
        }

    def _edge_colors(self):
        """
        The color of every edge, by force state or by edge type.
        """
        topology = self.topology

        if self.edge_colors == "type":
            return {edge: self._edge_typecolor(edge) for edge in topology.edges()}

        cmap = self.edge_statecolors
        colors = {}

        for edge in topology.edges():
            if topology.is_auxiliary_trail_edge(edge):
                colors[edge] = cmap["auxiliary_trail"]
                continue

            name = "length" if topology.is_trail_edge(edge) else "force"
            colors[edge] = cmap[copysign(1.0, topology.edge_attribute(edge, name))]

        return colors

    def _edge_typecolor(self, edge):
        """
        The color of an edge by its type, splitting deviation edges.

        Notes
        -----
        Direct and indirect deviation edges are told apart only once the trails
        have been built, because the distinction is drawn from the sequence the
        two end nodes belong to.
        """
        topology = self.topology
        cmap = self.edge_typecolors

        if topology.is_auxiliary_trail_edge(edge):
            return cmap["auxiliary_trail"]

        if topology.is_trail_edge(edge):
            return cmap["edge_trail"]

        if topology.has_trails() and topology.is_indirect_deviation_edge(edge):
            return cmap["edge_deviation_indirect"]

        return cmap["edge_deviation"]

    def edge_linestyles(self):
        """
        Draw the trail edges solid and the deviation edges dashed.
        """
        topology = self.topology

        return {
            edge: self.linestyles[topology.edge_attribute(edge, "type")]
            for edge in topology.edges()
        }

    def draw_forces(self):
        """
        Draw the loaded nodes as crosses inscribed in a circle.

        Notes
        -----
        The crosses are drawn straight onto the canvas rather than added to the
        scene, because a line scene object fixes its own stacking order and
        would end up underneath the opaque node markers.
        """
        if not self.show_loads:
            return

        topology = self.topology
        radius = self._node_radius()

        flips = (-1, 1)
        angle = pi / 4.0
        axis = [0.0, 0.0, 1.0]

        segments = []
        for node in topology.loaded_nodes():
            xyz = topology.node_coordinates(node)

            for flip in flips:
                line = Line(*[add_vectors(xyz, [radius * f, 0.0, 0.0]) for f in flips])
                rotation = Rotation.from_axis_and_angle(
                    axis=axis, angle=flip * angle, point=xyz
                )
                line.transform(rotation)

                segments.append([line.start[:2], line.end[:2]])

        if not segments:
            return

        collection = LineCollection(
            segments,
            linewidths=0.3,
            colors=[to_rgb(Color.black())] * len(segments),
            zorder=4000,
        )
        self.axes.add_collection(collection)
        self._mpl_objects.append(collection)

    def node_textlabel_formatters(self):
        """
        The supported node label tags and the formatter of each.
        """
        formatters = super(TopologyPlotterObject, self).node_textlabel_formatters()
        topology = self.topology

        def type_format(node):
            return "{}".format(topology.node_attribute(node, "type"))

        def sequence_format(node):
            return "{}".format(topology.node_sequence(node))

        def key_sequence_format(node):
            return "{}\n{}".format(node, sequence_format(node))

        formatters.update(
            {
                "type": type_format,
                "sequence": sequence_format,
                "keysequence": key_sequence_format,
            }
        )

        return formatters

    def edge_textlabel_formatters(self):
        """
        The supported edge label tags and the formatter of each.
        """
        precision = self.float_precision
        topology = self.topology

        def force_format(edge):
            return "{0:.{1}}".format(fabs(topology.edge_force(edge)), precision)

        def length_format(edge):
            return "{0:.{1}}".format(fabs(topology.edge_length_2(edge)), precision)

        def force_length_format(edge):
            return "f: {}\nl: {}".format(force_format(edge), length_format(edge))

        def state_format(edge):
            if topology.is_trail_edge(edge):
                parameter = topology.edge_length_2(edge)
            else:
                parameter = topology.edge_force(edge)
            return "{0:.{1}}".format(copysign(1.00, parameter), precision)

        def type_format(edge):
            return "{}".format(topology.edge_attribute(edge, "type"))

        def force_length_state_format(edge):
            return "f: {}\nl: {}\ns: {}".format(
                force_format(edge), length_format(edge), state_format(edge)
            )

        return {
            "force": force_format,
            "length": length_format,
            "state": state_format,
            "forcelength": force_length_format,
            "forcelengthstate": force_length_state_format,
            "type": type_format,
        }


def register_plotter_scene_objects():
    """
    Register the diagram scene objects with the plotter context.
    """
    register(FormDiagram, FormPlotterObject, context="Plotter")
    register(TopologyDiagram, TopologyPlotterObject, context="Plotter")
