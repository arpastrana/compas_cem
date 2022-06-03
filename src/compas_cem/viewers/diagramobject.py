from math import copysign
from math import fabs

from compas.colors import Color

from compas.geometry import add_vectors
from compas.geometry import length_vector
from compas.geometry import scale_vector
from compas.geometry import normalize_vector
from compas.geometry import translate_points

from compas.geometry import Vector
from compas.geometry import Point

from compas.utilities import geometric_key

from compas_cem import COLORS

from compas_view2.objects import NetworkObject
from compas_view2.shapes import Text


__all__ = ["DiagramObject"]

# ------------------------------------------------------------------------------
# Properties
# ------------------------------------------------------------------------------


class DiagramObject(NetworkObject):
    """Object to draw a diagram data structure in a viewer.

    Parameters
    ----------
    network : :class:`~compas_cem.diagrams.Diagram`
        A COMPAS CEM diagram.
    nodes : list[int], optional
        A list of node identifiers.
        Default is None, in which case all nodes are drawn.
    edges : list[tuple[int, int]], optional
        A list of edge keys (as uv pairs) identifying which edges to draw.
        The default is None, in which case all edges are drawn.
    nodecolor : :class:`~compas.colors.Color` | dict[hashable, :class:`~compas.colors.Color`], optional
        The color specification for the nodes.
    edgecolor : :class:`~compas.colors.Color` | dict[tuple[hashable, hashable]], :class:`~compas.colors.Color`], optional
        The color specification for the edges.
    node_size : float, optional
        The global node size.
        The default is None, and nodes are assigned :attr:`default_nodesize`.
    edge_width : float, optional
        The global edge width.
        The default is None, and nones are assigned :attr:`default_edgewidth`.

    Attributes
    ----------
    network : :class:`~compas_cem.diagrams.Diagram`
        The COMPAS CEM diagram associated with the object.
    nodes : list[int]
        The list of nodes to draw.
        Defaults to all nodes.
    edges : list[tuple[int, int]]
        The list of edges to draw.
        Default is a list of all edges of the network.
    node_color : dict[int, :class:`~compas.colors.Color`]
        Mapping between nodes and RGB color values.
        Missing nodes get the default node color :attr:`default_nodecolor`.
    edge_color : dict[tuple[int, int], :class:`~compas.colors.Color`]
        Mapping between edges and colors.
        Missing edges get the default edge color :attr:`default_edgecolor`.
    node_text : dict[int, str]
        Mapping between nodes and text labels.
    edge_text : dict[tuple[int, int], str]
        Mapping between edges and text labels.
    node_size : float
        The global node size.
        If missing, it defaults to the default node size :attr:`default_nodesize`.
    edge_width : float
        The global edge width.
        If missing, it defaults to the default edge width :attr:`default_edgewidth`.

    Class Attributes
    ----------------
    default_nodecolor : :class:`~compas.colors.Color`
        The default color for nodes that do not have a specified color.
    default_edgecolor : :class:`~compas.colors.Color`
        The default color for edges that do not have a specified color.
    default_nodesize : float
        The default size for nodes that do not have a specified size.
    default_edgewidth : float
        The default width for edges that do not have a specified width.

    """
    default_nodecolor = Color.from_rgb255(*COLORS["node_black"]).rgb
    default_edgecolor = Color.from_rgb255(*COLORS["edge"]).rgb
    default_loadcolor = Color.from_rgb255(*COLORS["load"]).rgb
    default_residualcolor = Color.from_rgb255(*COLORS["support_force"]).rgb

    support_nodecolor = Color.from_rgb255(*COLORS["node_support"]).rgb

    default_nodesize = 10.0
    default_edgewidth = 2.0
    default_nodexyz = [0.0, 0.0, 0.0]

    default_loadscale = 1.0
    default_loadtol = 1e-3
    default_residualscale = 1.0
    default_residualtol = 1e-3

    default_loadattrs = ["qx", "qy", "qz"]
    default_residualattrs = ["rx", "ry", "rz"]

    default_textcolor = Color.black().rgb
    default_textsize = 30
    default_floatprecision = "2f"

    def __init__(self,
                 diagram,
                 viewer=None,
                 nodes=None,
                 edges=None,
                 nodetext=None,
                 edgetext=None,
                 nodesize=None,
                 edgewidth=None,
                 loadscale=None,
                 residualscale=None,
                 loadtol=None,
                 residualtol=None,
                 show_nodes=True,
                 show_edges=True,
                 show_loads=True,
                 show_residuals=True,
                 show_nodetext=False,
                 show_edgetext=False,
                 text_size=None,
                 text_color=None,
                 **kwargs):

        super(DiagramObject, self).__init__(diagram, **kwargs)

        self._diagram = None

        self._nodes = None
        self._edges = None
        self._node_xyz = None
        self._node_color = None
        self._edge_color = None
        self._node_text = None
        self._edge_text = None
        self._edge_width = None
        self._node_size = None
        self._load_scale = None
        self._load_tol = None
        self._residual_scale = None
        self._residual_tol = None
        self._show_nodes = None
        self._show_edges = None

        self.diagram = diagram

        self.nodes = nodes
        self.edges = edges
        self.node_size = nodesize
        self.edge_width = edgewidth
        self.node_text = nodetext
        self.edge_text = edgetext
        self.load_scale = loadscale
        self.load_tol = loadtol
        self.residual_scale = residualscale
        self.residual_tol = residualtol

        self.show_nodes = show_nodes
        self.show_edges = show_edges
        self.show_loads = show_loads
        self.show_residuals = show_residuals
        self.show_nodetext = show_nodetext
        self.show_edgetext = show_edgetext

        self.text_size = text_size or self.default_textsize
        self.text_color = text_color or self.default_textcolor

        self.viewer = viewer

        # TODO: Is adding these commands here a good idea?
        self.draw_loads()
        self.draw_residuals()
        self.draw_nodetext()
        self.draw_edgetext()

# ------------------------------------------------------------------------------
# Properties
# ------------------------------------------------------------------------------

    @property
    def diagram(self):
        return self._diagram

    @diagram.setter
    def diagram(self, diagram):
        self._diagram = diagram
        self._nodes = None
        self._edges = None

    @property
    def nodes(self):
        if self._nodes is None:
            self._nodes = list(self.diagram.nodes())
        return self._nodes

    @nodes.setter
    def nodes(self, nodes):
        self._nodes = nodes

    @property
    def edges(self):
        if self._edges is None:
            self._edges = list(self.diagram.edges())
        return self._edges

    @edges.setter
    def edges(self, edges):
        self._edges = edges

    @property
    def node_xyz(self):
        if not self._node_xyz:
            self._node_xyz = {node: self.diagram.node_coordinates(node) for node in self.diagram.nodes()}
        return self._node_xyz

    @node_xyz.setter
    def node_xyz(self, node_xyz):
        self._node_xyz = node_xyz

    @property
    def node_size(self):
        if not self._node_size:
            self._node_size = self.default_nodesize
        return self._node_size

    @node_size.setter
    def node_size(self, nodesize):
        if isinstance(nodesize, (int, float)):
            self._node_size = nodesize
            self.pointsize = nodesize  # COMPAS View 2 API

    @property
    def node_color(self):
        if not self._node_color:
            self._node_color = {node: self.default_nodecolor for node in self.diagram.nodes()}
        return self._node_color

    @property
    def edge_color(self):
        if not self._edge_color:
            self._edge_color = {node: self.default_edgecolor for node in self.diagram.edges()}
        return self._edge_color

    @property
    def node_text(self):
        if not self._node_text:
            self._node_text = {node: str(node) for node in self.diagram.nodes()}
        return self._node_text

    @node_text.setter
    def node_text(self, text):
        if isinstance(text, str):
            if text == 'key':
                self._node_text = {node: str(node) for node in self.diagram.nodes()}
            else:
                self._node_text = self._node_textlabel(text)
        elif isinstance(text, dict):
            self._node_text = text

    @property
    def edge_text(self):
        if not self._edge_text:
            self._edge_text = {edge: "{}-{}".format(*edge) for edge in self.diagram.edges()}
        return self._edge_text

    @edge_text.setter
    def edge_text(self, text):
        if isinstance(text, str):
            if text == 'key':
                self._edge_text = {edge: "{}-{}".format(*edge) for edge in self.diagram.edges()}
            else:
                self._edge_text = self._edge_textlabel(text)
        elif isinstance(text, dict):
            self._edge_text = text

    @property
    def edge_width(self):
        if not self._edge_width:
            self._edge_width = self.default_edgewidth
        return self._edge_width

    @edge_width.setter
    def edge_width(self, edgewidth):
        if isinstance(edgewidth, (int, float)):
            self._edge_width = edgewidth
            self.linewidth = edgewidth

    @property
    def load_scale(self):
        if not self._load_scale:
            self._load_scale = self.default_loadscale
        return self._load_scale

    @load_scale.setter
    def load_scale(self, scale):
        if isinstance(scale, (int, float)):
            self._load_scale = scale

    @property
    def load_tol(self):
        if not self._load_tol:
            self._load_tol = self.default_loadtol
        return self._load_tol

    @load_tol.setter
    def load_tol(self, tol):
        if isinstance(tol, (int, float)):
            self._load_tol = tol

    @property
    def residual_scale(self):
        if not self._residual_scale:
            self._residual_scale = self.default_residualscale
        return self._residual_scale

    @residual_scale.setter
    def residual_scale(self, scale):
        if isinstance(scale, (int, float)):
            self._residual_scale = scale

    @property
    def residual_tol(self):
        if not self._residual_tol:
            self._residual_tol = self.default_residualtol
        return self._residual_tol

    @residual_tol.setter
    def residual_tol(self, tol):
        if isinstance(tol, (int, float)):
            self._residual_tol = tol

    @property
    def show_nodes(self):
        return self._show_nodes

    @show_nodes.setter
    def show_nodes(self, shownodes):
        if isinstance(shownodes, bool):
            self._show_edges = shownodes
            self.show_points = shownodes

    @property
    def show_edges(self):
        return self._show_edges

    @show_edges.setter
    def show_edges(self, showedges):
        if isinstance(showedges, bool):
            self._show_edges = showedges
            self.show_lines = showedges

# ------------------------------------------------------------------------------
# Draw stuff
# ------------------------------------------------------------------------------

    def draw_nodes(self):
        """
        Draw nodes.
        """
        positions = []
        colors = []
        elements = []

        for i, node in enumerate(self.nodes):
            positions.append(self.node_xyz.get(node, self.default_nodexyz))
            colors.append(self.node_color.get(node, self.default_nodecolor))
            elements.append([i])

        return positions, colors, elements

    def draw_edges(self):
        """
        Draw edges.
        """
        positions = []
        colors = []
        elements = []

        i = 0
        for node_u, node_v in self.edges:

            positions.append(self.node_xyz.get(node_u, self.default_nodexyz))
            positions.append(self.node_xyz.get(node_v, self.default_nodexyz))

            color = self.edge_color.get((node_u, node_v), self.default_edgecolor)
            colors.append(color)
            colors.append(color)

            elements.append([i + 0, i + 1])
            i += 2

        return positions, colors, elements

    def draw_loads(self):
        """
        Draw the loads.
        """
        if not self.show_loads:
            return

        if not self.viewer:
            print("No viewer found as DiagramObject attribute. Cannot draw loads!")
            return

        loads = self._force_vectors(nodes=self.nodes,
                                    scale=self.load_scale,
                                    tol=self.load_tol,
                                    attr_names=self.default_loadattrs,
                                    shift={})

        for load in loads.values():
            self.viewer.add(load["vector"],
                            position=load["point"],
                            size=load["vector"].length,
                            color=self.default_loadcolor)

    def draw_residuals(self):
        """
        Draw the residual forces at the nodes of a diagram.
        """
        # TODO: How to do shifts with vectors in compas_view?
        # Maybe draw custom arrows as lines + cone?
        def reaction_shifts():
            # TODO: needs a more robust check for arrow orientation
            # what we need is to know whether the arrow needs a full shift.
            # here we say we shift if the connected trail edge is in compression
            shift = {}
            for key in self.nodes:
                # every support must connect to only one trail edge
                s = False
                forces = [self.diagram.edge_force(e) for e in self.diagram.connected_edges(key)]
                max_force = max(forces, key=lambda f: fabs(f))
                if max_force < 0.0:
                    s = True
                shift[key] = s
            return shift

        if not self.show_residuals:
            return

        if not self.viewer:
            print("No viewer found as DiagramObject attribute. Cannot draw residuals!")
            return

        # TODO: How to do residual vector shifts?
        residuals = self._force_vectors(nodes=self.nodes,
                                        scale=self.residual_scale,
                                        tol=self.residual_tol,
                                        attr_names=self.default_residualattrs,
                                        shift={})  # shift=reaction_shifts())

        for residual in residuals.values():

            self.viewer.add(residual["vector"],
                            position=residual["point"],
                            size=residual["vector"].length,
                            color=self.default_residualcolor)

    def draw_nodetext(self):
        """
        Draw text on the nodes.
        """
        if not self.show_nodetext:
            return

        if not self.viewer:
            print("No viewer found as DiagramObject attribute. Cannot draw node labels!")
            return

        for node in self.nodes:
            label = self.node_text.get(node)
            text = Text(label,
                        self.diagram.node_coordinates(node),
                        height=self.text_size)
            self.viewer.add(text, color=self.text_color)

    def draw_edgetext(self):
        """
        Draw text on the edges.
        """
        if not self.show_edgetext:
            return

        if not self.viewer:
            print("No viewer found as DiagramObject attribute. Cannot draw edge labels!")
            return

        for edge in self.edges:
            u, v = edge
            label = self.edge_text.get(edge, self.edge_text.get(v, u))
            text = Text(label,
                        self.diagram.edge_midpoint(u, v),
                        height=self.text_size)
            self.viewer.add(text, color=self.text_color)

# ------------------------------------------------------------------------------
# Helper funtions
# ------------------------------------------------------------------------------

    def _force_vectors(self, nodes, attr_names, scale, shift, tol):
        """
        Compute forces (loads or residual forces) acting on a diagram as scaled vectors.

        Parameters
        ----------
        nodes : ``list``
            The list of node identifiers where to draw forces.
        attr_names : ``list``
            The attribute names of the force vector to draw.
        scale : ``float``
            The forces scale factor.
        shift : ``bool``
            A flag to shift an arrow one length along its own axis.
        tol : ``float``
            The minimum force magnitude to draw.

        Returns
        -------
        forces: ``dict``
            A dictionary with the arrows.
            Every arrow is described by a force vector, a start point.
        """
        forces = {}
        for node in nodes:

            force = {}

            f_vec = self.diagram.node_attributes(node, attr_names)
            f_vec_norm = normalize_vector(f_vec)
            f_vec_scaled = scale_vector(f_vec, scale)
            f_len = length_vector(f_vec)

            # skip if force is smaller than tolerance
            if f_len < tol:
                continue

            start = self.diagram.node_coordinates(node)
            end = add_vectors(start, f_vec_scaled)

            # shift
            # gap_arrow = self.node_size[node]
            force_shift = shift.get(node)
            if force_shift:
                # gap_arrow = (gap_arrow + length_vector(f_vec_scaled)) * -1
                gap_arrow = length_vector(f_vec_scaled) * -1
                gap_vector = scale_vector(f_vec_norm, gap_arrow)
                start, end = translate_points([start, end], gap_vector)

            force["point"] = Point(*start)
            force["vector"] = Vector.from_start_end(start, end)

            forces[node] = force

        return forces

    def _node_textlabel(self, text_tag):
        """
        Generate text labels to plot on the nodes of a diagram.

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
            return geometric_key(self.diagram.node_coordinates(x), self.default_floatprecision)

        def key_gkey_format(x):
            return "{}\n{}".format(x, gkey_format(x))

        def type_format(x):
            return "{}".format(self.topology.node_attribute(x, "type"))

        tags_formatter = {"xyz": gkey_format,
                          "keyxyz": key_gkey_format,
                          "type": type_format}

        if text_tag not in tags_formatter:
            return

        text_labels = {}
        formatter = tags_formatter[text_tag]

        for node in self.nodes:
            label = formatter(node)
            text_labels[node] = label

        return text_labels

    def _edge_textlabel(self, text_tag):
        """
        Generate text labels to plot on the edges of a diagram.

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
            return "{0:.{1}}".format(fabs(self.diagram.edge_force(x)), self.default_floatprecision)

        def length_format(x):
            return "{0:.{1}}".format(fabs(self.diagram.edge_length_2(x)), self.default_floatprecision)

        def force_length_format(x):
            return "f: {}\nl: {}".format(force_format(x), length_format(x))

        def state_format(x):
            if self.diagram.is_trail_edge(x):
                parameter = self.diagram.edge_length_2(edge)
            else:
                parameter = self.diagram.edge_force(edge)
            state = copysign(1.00, parameter)
            return "{0:.{1}}".format(state, self.default_floatprecision)

        def type_format(x):
            return "{}".format(self.diagram.edge_attribute(x, "type"))

        def force_length_state_format(x):
            return "f: {}\nl: {}\ns: {}".format(force_format(x), length_format(x), state_format(x))

        tags_formatter = {"force": force_format,
                          "length": length_format,
                          "state": state_format,
                          "forcelength": force_length_format,
                          "forcelengthstate": force_length_state_format,
                          "type": type_format}

        if text_tag not in tags_formatter:
            return

        text_labels = {}
        formatter = tags_formatter[text_tag]

        for edge in self.edges:
            label = formatter(edge)
            text_labels[edge] = label

        return text_labels

# ------------------------------------------------------------------------------
# COMPAS View2 Interface
# ------------------------------------------------------------------------------

    def _points_data(self):
        """
        Draw nodes.
        """
        return self.draw_nodes()

    def _lines_data(self):
        """
        Draw edges.
        """
        return self.draw_edges()
