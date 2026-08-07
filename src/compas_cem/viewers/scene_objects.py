from math import copysign
from math import fabs

from compas.colors import Color
from compas.geometry import Vector
from compas.geometry import add_vectors
from compas.geometry import length_vector
from compas.geometry import normalize_vector
from compas.geometry import scale_vector
from compas.geometry import translate_points
from compas.scene import register
from compas.tolerance import TOL
from compas_viewer.scene import GraphObject
from compas_viewer.scene import Tag

from compas_cem import COLORS
from compas_cem.diagrams import FormDiagram
from compas_cem.diagrams import TopologyDiagram

__all__ = [
    "DiagramObject",
    "FormDiagramObject",
    "TopologyDiagramObject",
    "register_viewer_scene_objects",
]


def _color(name):
    """
    Look a package color up as a COMPAS color.
    """
    return Color.from_rgb255(*COLORS[name])


class DiagramObject(GraphObject):
    """
    A scene object that draws a diagram in a viewer.

    Parameters
    ----------
    nodetext :
        A tag naming what to label the nodes with, or a mapping of nodes to
        labels.
    edgetext :
        A tag naming what to label the edges with, or a mapping of edges to
        labels.
    loadscale :
        The factor to scale the load vectors by.
    loadtol :
        The smallest load magnitude worth drawing.
    residualscale :
        The factor to scale the residual force vectors by.
    residualtol :
        The smallest residual force magnitude worth drawing.
    show_loads :
        Whether to draw the loads.
    show_residuals :
        Whether to draw the residual forces.
    show_nodetext :
        Whether to draw the node labels.
    show_edgetext :
        Whether to draw the edge labels.
    textsize :
        The height of the labels.
    textcolor :
        The color of the labels.

    Notes
    -----
    The loads, the residual forces and the labels are added as children of this
    object, so they follow it when it is shown, hidden or removed.
    """

    loadcolor = _color("load")
    residualcolor = _color("support_force")
    support_nodecolor = _color("node_support")
    default_nodecolor = _color("node_black")
    default_edgecolor = _color("edge")

    load_attrs = ["qx", "qy", "qz"]
    residual_attrs = ["rx", "ry", "rz"]

    float_precision = "2f"

    def __init__(
        self,
        nodetext=None,
        edgetext=None,
        loadscale=1.0,
        loadtol=1e-3,
        residualscale=1.0,
        residualtol=1e-3,
        show_loads=True,
        show_residuals=True,
        show_nodetext=False,
        show_edgetext=False,
        textsize=50,
        textcolor=None,
        **kwargs,
    ):
        super(DiagramObject, self).__init__(**kwargs)

        self.load_scale = loadscale
        self.load_tol = loadtol
        self.residual_scale = residualscale
        self.residual_tol = residualtol

        self.show_loads = show_loads
        self.show_residuals = show_residuals
        self.show_nodetext = show_nodetext
        self.show_edgetext = show_edgetext

        self.textsize = textsize
        self.textcolor = textcolor or Color.black()

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

    def node_colors(self):
        """
        The color of every node.

        Returns
        -------
        colors :
            A mapping of nodes to colors.
        """
        raise NotImplementedError

    def edge_colors(self):
        """
        The color of every edge.

        Returns
        -------
        colors :
            A mapping of edges to colors.
        """
        raise NotImplementedError

    # ==========================================================================
    # Buffers
    # ==========================================================================

    def _read_points_data(self):
        """
        The node positions and their colors, for the point buffer.
        """
        diagram = self.diagram
        colors = self.node_colors()

        positions = []
        rgb = []
        elements = []

        for i, node in enumerate(diagram.nodes()):
            positions.append(diagram.node_coordinates(node))
            rgb.append(colors.get(node, self.default_nodecolor))
            elements.append([i])

        return positions, rgb, elements

    def _read_lines_data(self):
        """
        The edge end points and their colors, for the line buffer.
        """
        diagram = self.diagram
        colors = self.edge_colors()

        positions = []
        rgb = []
        elements = []

        i = 0
        for edge in diagram.edges():
            u, v = edge
            color = colors.get(edge, self.default_edgecolor)

            positions.append(diagram.node_coordinates(u))
            positions.append(diagram.node_coordinates(v))
            rgb.append(color)
            rgb.append(color)
            elements.append([i + 0, i + 1])
            i += 2

        return positions, rgb, elements

    # ==========================================================================
    # Draw
    # ==========================================================================

    def draw(self):
        """
        Draw the diagram, its forces and its labels.
        """
        super(DiagramObject, self).draw()

        if self.show_loads:
            self.draw_loads()
        if self.show_residuals:
            self.draw_residuals()
        if self.show_nodetext:
            self.draw_nodetext()
        if self.show_edgetext:
            self.draw_edgetext()

    def draw_loads(self):
        """
        Draw the loads applied to the nodes as arrows.
        """
        self._draw_force_vectors(
            attr_names=self.load_attrs,
            scale=self.load_scale,
            tol=self.load_tol,
            color=self.loadcolor,
            shift={node: False for node in self.diagram.nodes()},
        )

    def draw_residuals(self):
        """
        Draw the residual forces at the nodes as arrows.
        """
        self._draw_force_vectors(
            attr_names=self.residual_attrs,
            scale=self.residual_scale,
            tol=self.residual_tol,
            color=self.residualcolor,
            shift=self._residual_shifts(),
        )

    def draw_nodetext(self):
        """
        Draw the labels of the nodes.
        """
        labels = self.node_textlabels(self._nodetext_tag)
        if labels is None:
            labels = {node: str(node) for node in self.diagram.nodes()}

        for node, label in labels.items():
            tag = Tag(
                str(label),
                self.diagram.node_coordinates(node),
                color=self.textcolor,
                height=self.textsize,
            )
            self.add(tag)

    def draw_edgetext(self):
        """
        Draw the labels of the edges.
        """
        labels = self.edge_textlabels(self._edgetext_tag)
        if labels is None:
            labels = {edge: "{}-{}".format(*edge) for edge in self.diagram.edges()}

        for edge, label in labels.items():
            tag = Tag(
                str(label),
                self.diagram.edge_midpoint(edge),
                color=self.textcolor,
                height=self.textsize,
            )
            self.add(tag)

    def _draw_force_vectors(self, attr_names, scale, tol, color, shift):
        """
        Draw a force at every node as a scaled arrow.

        Parameters
        ----------
        attr_names :
            The node attributes that hold the force vector.
        scale :
            The factor to scale the force vectors by.
        tol :
            The smallest force magnitude worth drawing.
        color :
            The color to draw the arrows in.
        shift :
            A mapping of nodes to whether the arrow is shifted one length along
            its own axis.
        """
        diagram = self.diagram

        for node in diagram.nodes():
            vector = diagram.node_attributes(node, attr_names)
            if length_vector(vector) < tol:
                continue

            scaled = scale_vector(vector, scale)
            start = diagram.node_coordinates(node)
            end = add_vectors(start, scaled)

            if shift.get(node):
                gap = scale_vector(normalize_vector(vector), -length_vector(scaled))
                start, end = translate_points([start, end], gap)

            arrow = Vector.from_start_end(start, end)
            self.add(arrow, anchor=start, linecolor=color, facecolor=color)

    def _residual_shifts(self):
        """
        Whether the residual arrow at every node points back into its trail.

        Notes
        -----
        A residual is shifted when the strongest edge meeting the node is in
        compression, so the arrow reads as pushing against the support rather
        than pulling away from it.

        TODO: needs a more robust check for arrow orientation. What is wanted
        is to know whether the arrow needs a full shift.
        """
        diagram = self.diagram
        shifts = {}

        for node in diagram.nodes():
            forces = [diagram.edge_force(e) for e in diagram.node_connected_edges(node)]
            if not forces:
                shifts[node] = False
                continue
            shifts[node] = max(forces, key=lambda f: fabs(f)) < 0.0

        return shifts

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

        def type_format(node):
            return "{}".format(diagram.node_attribute(node, "type"))

        return {
            "xyz": gkey_format,
            "keyxyz": key_gkey_format,
            "type": type_format,
        }

    def edge_textlabel_formatters(self):
        """
        The supported edge label tags and the formatter of each.
        """
        precision = self.float_precision
        diagram = self.diagram

        def force_format(edge):
            return "{0:.{1}}".format(diagram.edge_force(edge), precision)

        def length_format(edge):
            return "{0:.{1}}".format(diagram.edge_length_2(edge), precision)

        def force_length_format(edge):
            return "f: {}\nl: {}".format(force_format(edge), length_format(edge))

        def state_format(edge):
            parameter = diagram.edge_force(edge)
            return "{0:.{1}}".format(copysign(1.00, parameter), precision)

        return {
            "force": force_format,
            "length": length_format,
            "state": state_format,
            "forcelength": force_length_format,
        }


class FormDiagramObject(DiagramObject):
    """
    A scene object that draws a form diagram in a viewer.
    """

    edgecolor_tension = _color("tension")
    edgecolor_compression = _color("compression")

    @property
    def form(self):
        """
        The form diagram this object draws.
        """
        return self.graph

    def node_colors(self):
        """
        Color the support nodes apart from the rest.
        """
        form = self.form

        return {
            node: (
                self.support_nodecolor
                if form.is_node_support(node)
                else self.default_nodecolor
            )
            for node in form.nodes()
        }

    def edge_colors(self):
        """
        Color the edges by whether they are in tension or in compression.
        """
        form = self.form
        colors = {}

        for edge in form.edges():
            force = form.edge_force(edge)
            if force >= 0.0:
                colors[edge] = self.edgecolor_tension
            else:
                colors[edge] = self.edgecolor_compression

        return colors


class TopologyDiagramObject(DiagramObject):
    """
    A scene object that draws a topology diagram in a viewer.
    """

    edgecolor_trail = _color("edge_trail")
    edgecolor_deviation = _color("edge_deviation")
    edgecolor_deviation_indirect = _color("edge_deviation_indirect")
    edgecolor_auxiliary = _color("auxiliary_trail")
    origin_nodecolor = _color("node_origin")

    @property
    def topology(self):
        """
        The topology diagram this object draws.
        """
        return self.graph

    def node_colors(self):
        """
        Color the support and the origin nodes apart from the rest.
        """
        topology = self.topology
        colors = {}

        for node in topology.nodes():
            if topology.is_node_support(node):
                colors[node] = self.support_nodecolor
            elif topology.is_node_origin(node):
                colors[node] = self.origin_nodecolor
            else:
                colors[node] = self.default_nodecolor

        return colors

    def edge_colors(self):
        """
        Color the edges by their type.

        Notes
        -----
        Direct and indirect deviation edges are told apart only once the trails
        have been built, because the distinction is drawn from the sequence the
        two end nodes belong to.
        """
        topology = self.topology
        colors = {}

        for edge in topology.edges():
            if topology.is_auxiliary_trail_edge(edge):
                colors[edge] = self.edgecolor_auxiliary
            elif topology.is_trail_edge(edge):
                colors[edge] = self.edgecolor_trail
            elif topology.has_trails() and topology.is_indirect_deviation_edge(edge):
                colors[edge] = self.edgecolor_deviation_indirect
            else:
                colors[edge] = self.edgecolor_deviation

        return colors

    def edge_textlabel_formatters(self):
        """
        The supported edge label tags and the formatter of each.
        """
        formatters = super(TopologyDiagramObject, self).edge_textlabel_formatters()
        precision = self.float_precision
        topology = self.topology

        def state_format(edge):
            if topology.is_trail_edge(edge):
                parameter = topology.edge_length_2(edge)
            else:
                parameter = topology.edge_force(edge)
            return "{0:.{1}}".format(copysign(1.00, parameter), precision)

        def type_format(edge):
            return "{}".format(topology.edge_attribute(edge, "type"))

        formatters.update({"state": state_format, "type": type_format})

        return formatters


def register_viewer_scene_objects():
    """
    Register the diagram scene objects with the viewer context.
    """
    register(FormDiagram, FormDiagramObject, context="Viewer")
    register(TopologyDiagram, TopologyDiagramObject, context="Viewer")
