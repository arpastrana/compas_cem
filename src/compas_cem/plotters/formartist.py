import matplotlib.pyplot as plt

from math import copysign
from math import fabs

from compas.geometry import add_vectors
from compas.geometry import length_vector
from compas.geometry import scale_vector
from compas.geometry import normalize_vector
from compas.geometry import translate_points

from compas.geometry import Vector
from compas.geometry import Point

from compas.utilities import geometric_key

from compas_plotters.artists import NetworkArtist

from compas_cem import COLORS


__all__ = ["FormArtist"]


class FormArtist(NetworkArtist):
    """
    An artist that draws a form diagram.

    Parameters
    ----------
    form_diagram : :class:`compas_cem.diagrams.FormDiagram`
        The form diagram to plot.
    """
    def __init__(self,
                 form_diagram,
                 nodetext=None,
                 edgetext=None,
                 loadtol=1e-3,
                 loadscale=1.0,
                 reactiontol=1e-3,
                 reactionscale=1.0,
                 show_loads=True,
                 show_reactions=True,
                 show_nodetext=False,
                 show_edgetext=False,
                 **kwargs):
        super(FormArtist, self).__init__(form_diagram, **kwargs)

        self._edge_state_colors = {-1: COLORS["compression"],
                                   1: COLORS["tension"],
                                   0: COLORS["edge"]}

        self._node_colors = {"support": COLORS["node_support"],
                             "default": COLORS["node"]}

        self._form = self.network

        self._float_precision = "2f"

        self.load_color = COLORS["load"]
        self.load_attrs = ["qx", "qy", "qz"]
        self.load_tol = loadtol
        self.load_scale = loadscale

        self.reaction_color = COLORS["support_force"]
        self.reaction_attrs = ["rx", "ry", "rz"]
        self.reaction_tol = reactiontol
        self.reaction_scale = reactionscale

        self.edge_text = self._edge_textlabel(edgetext)
        self.node_text = self._node_textlabel(nodetext)

        self.show_loads = show_loads
        self.show_reactions = show_reactions
        self.show_nodetext = show_nodetext
        self.show_edgetext = show_edgetext


    @property
    def form(self):
        """
        The form diagram to plot.

        Returns
        -------
        form : :class:`compas_cem.diagrams.FormDiagram`
            A form diagram.
        """
        return self._form

    @property
    def node_colors(self):
        """
        The colors to draw the nodes of a form diagram.

        Returns
        -------
        node_colors : ``dict`` of ``color``
            A dictionary that maps node type to RGB color.
        """
        return self._node_colors

    @property
    def edge_state_colors(self):
        """
        The default colors to draw edges based on the forces acting on them.

        Returns
        -------
        edge_state_colors : ``dict`` of ``color``
            For compression forces, blue (0, 0, 255).
            For tension force, red (255, 0, 0).
            No force, black (0, 0, 0).
        """
        return self._edge_state_colors

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

    def draw_nodes(self, **kwargs):
        """
        Draws the nodes of a ``FormDiagram``.

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
        all the nodes or edges in the ``FormDiagram``. If instead, a dictionary
        that maps ``{node_key: attribute}`` is supplied, specific values can be
        assigned individually.
        """
        cmap = self.node_colors

        text = kwargs.get("text")
        if text and text != "key":
            kwargs["text"] = self._text_labels_nodes(text)

        nc = {}
        for node in self.form.nodes():
            if self.form.is_node_support(node):
                nc[node] = cmap["support"]
            else:
                nc[node] = cmap["default"]

        super(FormArtist, self).draw_nodes(color=nc, **kwargs)

    def draw_edges(self, **kwargs):
        """
        Draws the edges of a ``FormDiagram``.

        Parameters
        ----------
        keys : ``list`` of ``tuple``
            The keys of the edges to plot.
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
        all the nodes or edges in the ``FormDiagram``. If instead, a dictionary
        that maps ``{edge_key: attribute}`` is supplied, specific values can be
        assigned individually.
        """
        cmap = self.edge_state_colors
        ec = {e: cmap[copysign(1.0, self.form.edge_attribute(e, "force") or 0.0)] for e in self.form.edges()}

        text = kwargs.get("text")
        if text and text != "key":
            kwargs["text"] = self._text_labels_edges(text)

        return super(FormArtist, self).draw_edges(color=ec, **kwargs)

    def draw_loads(self, nodes=None):
        """
        Draws the node loads in a ``FormDiagram`` as scaled arrows.

        Parameters
        ----------
        nodes : ``list``
            The list of node keys where to draw forces.
            If nodes is ``None``, all nodes are considered.
            Defaults to ``None``.
        """
        self._draw_forces(nodes=self.nodes,
                          attr_names=self.load_attrs,
                          scale=self.load_scale,
                          color=self.load_color,
                          tol=self.load_tol,
                          shift={key: False for key in self.nodes})

    def draw_reactions(self, keys=None):
        """
        Draws the support reaction forces in a ``FormDiagram`` as scaled arrows.

        Parameters
        ----------
        keys : ``list``
            The list of node keys where to draw forces.
            If nodes is ``None``, all nodes in will be considered.
            Defaults to ``None``.
        """
        def _reaction_shifts():
            # TODO: needs a more robust check for arrow orientation
            # what we need is to know whether the arrow needs a full shift.
            # here we say we shift if the connected trail edge is in compression
            shift = {}
            for key in self.nodes:
                # every support must connect to only one trail edge
                s = False
                forces = [self.form.edge_force(e) for e in self.form.connected_edges(key)]
                max_force = max(forces, key=lambda f: fabs(f))
                if max_force < 0.0:
                    s = True
                shift[key] = s
            return shift

        # keys = keys or list(self.form.support_nodes())
        self._draw_forces(nodes=self.nodes,
                          attr_names=self.reaction_attrs,
                          scale=self.reaction_scale,
                          color=self.reaction_color,
                          tol=self.reaction_tol,
                          shift=_reaction_shifts())

    def _draw_forces(self, nodes, attr_names, scale, color, shift, tol):
        """
        Draw forces (loads or reaction forces) as scaled arrows.

        Parameters
        ----------
        nodes : ``list``
            The list of node identifiers where to draw forces.
        attr_names : ``list``
            The attribute names of the force vector to draw.
        scale : ``float``
            The forces scale factor.
        color : ``tuple``
            The forces' color in rgb.
        shift : ``bool``
            A flag to shift an arrow one length along its own axis.
        tol : ``float``
            The minimum force magnitude to draw.
        """
        for node in nodes:

            q_vec = self.form.node_attributes(node, attr_names)
            q_vec_scaled = scale_vector(q_vec, scale)
            q_vec_norm = normalize_vector(q_vec)
            q_len = length_vector(q_vec)

            # skip if force is smaller than tolerance
            if q_len < tol:
                continue

            start = self.form.node_xyz(node)
            end = add_vectors(start, q_vec_scaled)

            # shift
            gap_arrow = self.node_size[node]
            if shift[node]:
                gap_arrow = (gap_arrow + length_vector(q_vec_scaled)) * -1

            gap_vector = scale_vector(q_vec_norm, gap_arrow)
            start, end = translate_points([start, end], gap_vector)

            start = Point(*start)
            force = Vector.from_start_end(start, end)

            self.plotter.add(force, point=start, color=color)

    def _node_textlabel(self, text_tag):
        """
        Generates text labels to plot on the nodes of a ``FormDiagram``.

        Input
        -----
        text_tag : `str`
            Tag query. Supported tags are: "xyz" and "key-xyz".

        Returns
        -------
        text_labels : ``dict``
            A dictionary of text labels
        """
        def gkey_format(x):
            return geometric_key(self.form.node_xyz(x), precision)

        def key_gkey_format(x):
            return "{} / {}".format(x, gkey_format(x))

        precision = self.float_precision

        tags_formatter = {"xyz": gkey_format,
                          "key-xyz": key_gkey_format}

        if text_tag not in tags_formatter:
            return None

        text_labels = {}
        formatter = tags_formatter[text_tag]

        for node in self.form.nodes():
            label = formatter(node)
            text_labels[node] = label

        return text_labels

    def _edge_textlabel(self, text_tag):
        """
        Generates text labels to plot on the edges of a ``FormDiagram``.

        Input
        -----
        text_tag : `str`
            Tag query.
            Supported tags are: "force", "length", and "force-length".

        Returns
        -------
        text_labels : ``dict``
            A dictionary of text labels
        """
        def force_format(x):
            return "{0:.{1}}".format(self.form.edge_force(x), precision)

        def length_format(x):
            return "{0:.{1}}".format(self.form.edge_length(*x), precision)

        def force_length_format(x):
            return "f: {} / lt: {}".format(force_format(x), length_format(x))

        precision = self.float_precision

        tags_formatter = {"force": force_format,
                          "length": length_format,
                          "force-length": force_length_format}

        if text_tag not in tags_formatter:
            return None

        text_labels = {}
        formatter = tags_formatter[text_tag]

        for edge in self.form.edges():
            label = formatter(edge)
            text_labels[edge] = label

        return text_labels

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
        if self.show_reactions:
            self.draw_reactions()
        if self.show_nodetext:
            self.draw_nodelabels()
        if self.show_edgetext:
            self.draw_edgelabels()

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


if __name__ == "__main__":
    pass
