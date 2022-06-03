from compas.colors import Color
from math import copysign

from compas.geometry import add_vectors
from compas.geometry import length_vector
from compas.geometry import scale_vector
from compas.geometry import normalize_vector
from compas.geometry import translate_points

from compas.geometry import Vector
from compas.geometry import Point

from compas_cem import COLORS

from compas_view2.objects import BufferObject
from compas_view2.objects import NetworkObject


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
    # default_nodecolor = Color.from_rgb255(0.0, 0.0, 0.0)
    default_nodecolor = [0.0, 0.0, 0.0]
    default_edgecolor = [255.0, 0.0, 0.0]
    default_loadcolor = COLORS["load"]
    default_residualcolor = COLORS["support_force"]

    default_nodexyz = [0.0, 0.0, 0.0]
    default_nodesize = 2.0
    default_edgewidth = 2.0
    default_loadscale = 1.0
    default_loadtol = 1e-3
    default_residualscale = 1.0
    default_residualtol = 1e-3

    default_loadattrs = ["qx", "qy", "qz"]
    default_residualattrs = ["rx", "ry", "rz"]

    def __init__(self,
                 diagram,
                 viewer=None,
                 nodes=None,
                 edges=None,
                 nodecolor=None,
                 edgecolor=None,
                 nodetext=None,
                 edgetext=None,
                 nodesize=None,
                 edgewidth=None,
                 loadscale=None,
                 loadtol=None,
                 show_nodes=True,
                 show_edges=True,
                 show_loads=True,
                 show_nodetext=False,
                 show_edgetext=False,
                 **kwargs):

        super(DiagramObject, self).__init__(diagram, color=Color.black(), **kwargs)

        self._diagram = None
        self._nodes = None
        self._edges = None
        self._node_color = None
        self._edge_color = None
        self._node_text = None
        self._edge_text = None
        self._edge_width = None

        self.diagram = diagram

        self.nodes = nodes
        self.edges = edges
        self.node_color = nodecolor or {}
        self.edge_color = edgecolor or {}
        self.node_size = nodesize
        self.edge_width = edgewidth

        self.viewer = viewer

        self.edge_statecolors = {-1: COLORS["compression"],
                                 1: COLORS["tension"],
                                 0: COLORS["edge"]}

        self.node_colortype = {"support": COLORS["node_support"],
                                "default": COLORS["node"]}


# ------------------------------------------------------------------------------
# Properties
# ------------------------------------------------------------------------------

    @property
    def diagram(self):
        return self._diagram

    @diagram.setter
    def diagram(self, diagram):
        self._diagram = diagram
        self._node_xyz = None

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
            return {node: self.diagram.node_attributes(node, 'xyz') for node in self.nodes}
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

    @property
    def node_text(self):
        if not self._node_text:
            self._node_text = {node: str(node) for node in self.nodes}
        return self._node_text

    @node_text.setter
    def node_text(self, text):
        if text == 'key':
            self._node_text = {node: str(node) for node in self.nodes}
        elif isinstance(text, dict):
            self._node_text = text

    @property
    def edge_text(self):
        if not self._edge_text:
            self._edge_text = {edge: "{}-{}".format(*edge) for edge in self.edges}
        return self._edge_text

    @edge_text.setter
    def edge_text(self, text):
        if text == 'key':
            self._edge_text = {edge: "{}-{}".format(*edge) for edge in self.diagram.edges()}
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

# ------------------------------------------------------------------------------
# Draw stuff
# ------------------------------------------------------------------------------

    def draw_nodes(self):
        """
        Draw nodes.
        """
        cmap = self.node_colortype
        nc = {}
        for node in self.nodes:
            if self.diagram.is_node_support(node):
                nc[node] = Color.from_rgb255(*cmap["support"])
            else:
                nc[node] = Color.black()

        self.node_color = nc
        self.pointcolors = nc

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
        cmap = self.edge_statecolors
        ec = {e: Color.from_rgb255(*cmap[copysign(1.0, self.diagram.edge_attribute(e, "force") or 0.0)]) for e in self.edges}

        self.edge_color = ec
        self.linecolors = ec

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
        if not self.viewer:
            print("No viewer found as DiagramObject attribute. Cannot draw loads!")
            return

        loads = self._compute_forces(nodes=self.nodes,
                                     attr_names=self.default_loadattrs,
                                     scale=self.loadscale,
                                     tol=self.load_tol,
                                     shift={key: False for key in self.nodes})

        for load in loads.items():
            self.viewer.add(load["vector"], position=load["point"], color=self.load_color)

    def _compute_forces(self, nodes, attr_names, scale, shift, tol):
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
            f_vec_scaled = scale_vector(f_vec, scale)
            f_vec_norm = normalize_vector(f_vec)
            f_len = length_vector(f_vec)

            # skip if force is smaller than tolerance
            if f_len < tol:
                continue

            start = self.diagram.node_coordinates(node)
            end = add_vectors(start, f_vec_scaled)

            # shift
            gap_arrow = self.node_size[node]
            if shift[node]:
                gap_arrow = (gap_arrow + length_vector(f_vec_scaled)) * -1

            gap_vector = scale_vector(f_vec_norm, gap_arrow)
            start, end = translate_points([start, end], gap_vector)

            force["point"] = Point(*start)
            force["vector"] = Vector.from_start_end(start, end)

            forces[node] = force

        return forces

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

    # @property
    # def pointcolors(self):
    #     return self.node_color

    # @property
    # def linecolors(self):
    #     return self.edge_color

    # @property
    # def default_color_points(self):
    #     return self.default_nodecolor

    # @property
    # def default_color_lines(self):
    #     return self.default_edgecolor
