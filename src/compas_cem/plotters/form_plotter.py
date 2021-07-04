import matplotlib.pyplot as plt

from math import copysign
from math import fabs

from compas.geometry import add_vectors
from compas.geometry import length_vector
from compas.geometry import scale_vector
from compas.geometry import normalize_vector
from compas.geometry import translate_points

from compas.utilities import geometric_key
from compas_plotters import NetworkPlotter

from compas_cem import COLORS


__all__ = ["FormPlotter"]


class FormPlotter(NetworkPlotter):
    """
    A plotter tailored to draw form-related matters.

    Parameters
    ----------
    form_diagram : :class:`compas_cem.diagrams.FormDiagram`
        The form diagram to plot.
    """
    def __init__(self, form_diagram, *args, **kwargs):
        super(FormPlotter, self).__init__(form_diagram, *args, **kwargs)

        self._edge_colors = {"trail": COLORS["edge"],
                             "deviation": COLORS["edge"]}

        self._edge_state_colors = {-1: COLORS["compression"],
                                   1: COLORS["tension"],
                                   0: COLORS["edge"]}

        self._form = self.datastructure
        self._float_precision = "3f"

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

    def draw_nodes(self, *args, **kwargs):
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
        fc = COLORS["node"]

        text = kwargs.get("text")
        if text and text != "key":
            kwargs["text"] = self._text_labels_nodes(text)

        super(FormPlotter, self).draw_nodes(facecolor=fc, *args, **kwargs)

    def draw_edges(self, *args, **kwargs):
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
        ds = self.datastructure
        cmap = self.edge_state_colors
        ec = {e: cmap[copysign(1.0, ds.edge_attribute(e, "force") or 0.0)] for e in ds.edges()}

        text = kwargs.get("text")
        if text and text != "key":
            kwargs["text"] = self._text_labels_edges(text)

        return super(FormPlotter, self).draw_edges(color=ec, *args, **kwargs)

    def draw_loads(self, keys=None, scale=1.0, width=1.0, gap=0.05, tol=1e-3):
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
            The arrows uniform display width. Defaults to ``1.0``.
        gap : ``float``
            The offset between the node and the load. Defaults to ``0.2``.
        tol : ``float``
            The minimum force magnitude to draw. Defaults to ``1e-3``.
        """
        if not keys:
            keys = list(self.datastructure.nodes())
        attrs = ["qx", "qy", "qz"]
        color = COLORS["load"]
        shift = {key: False for key in keys}
        self._draw_forces(keys, attrs, scale, color, width, shift, gap, tol)

    def draw_reactions(self, keys=None, scale=1.0, width=1.0, gap=0.05, tol=1e-3):
        """
        Draws the support reaction forces in a ``FormDiagram`` as scaled arrows.

        Parameters
        ----------
        keys : ``list``
            The list of node keys where to draw forces.
            If nodes is ``None``, all nodes in will be considered.
            Defaults to ``None``.
        scale : ``float``
            The scale of the residual arrows. Defaults to ``1.0``.
        width : ``float``
            The arrows uniform display width. Defaults to ``1.0``.
        gap : ``float``
            The offset between the node and the force. Defaults to ``0.2``.
        tol : ``float``
            The minimum force magnitude to draw. Defaults to ``1e-3``.
        """
        if not keys:
            keys = list(self.datastructure.support_nodes())
        attrs = ["rx", "ry", "rz"]
        color = COLORS["support_force"]

        # TODO: needs a more robust check for arrow orientation
        # what we need is to know whether the arrow needs a full shift.
        # here we say we shift if the connected trail edge is in compression
        form = self.datastructure
        shift = {}
        for key in keys:
            # every support must connect to only one trail edge
            s = False
            forces = [form.edge_force(e) for e in form.connected_edges(key)]
            max_force = max(forces, key=lambda f: fabs(f))
            if max_force < 0.0:
                s = True
            shift[key] = s

        self._draw_forces(keys, attrs, scale, color, width, shift, gap, tol)

    def _draw_forces(self, keys, attrs, scale, color, width, shift, gap, tol):
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

        super(FormPlotter, self).draw_arrows(arrows)

    def draw_segments(self, segments, color=(50, 50, 50), width=0.5, ls="--"):
        """
        Draws additional line segments on a ``FormDiagram``.

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

        lines = super(FormPlotter, self).draw_lines(lines)
        lines.set_linestyle(ls)

        return lines

    def _text_labels_nodes(self, text_tag):
        """
        Generates text labels to plot on the nodes of a ``FormDiagram``.

        Input
        -----
        text_tag : `str`
            Tag query. Supported tags are: "xyz" and "key-xyz".

        Returns
        -------
        text_labels : ``list``
            A list of text labels
        """
        def gkey_format(x):
            return geometric_key(ds.node_xyz(x), precision)

        def key_gkey_format(x):
            return "{} / {}".format(x, gkey_format(x))

        ds = self.datastructure
        precision = self.float_precision

        tags_formatter = {"xyz": gkey_format,
                          "key-xyz": key_gkey_format}

        if text_tag not in tags_formatter:
            return None

        text_labels = {}
        formatter = tags_formatter[text_tag]

        for node in ds.nodes():
            label = formatter(node)
            text_labels[node] = label

        return text_labels

    def _text_labels_edges(self, text_tag):
        """
        Generates text labels to plot on the edges of a ``FormDiagram``.

        Input
        -----
        text_tag : `str`
            Tag query.
            Supported tags are: "force", "length", and "force-length".

        Returns
        -------
        text_labels : ``list``
            A list of text labels
        """
        def force_format(x):
            return "{0:.{1}}".format(ds.edge_force(x), precision)

        def length_format(x):
            return "{0:.{1}}".format(ds.edge_length(*x), precision)

        def force_length_format(x):
            return "f: {} / lt: {}".format(force_format(x), length_format(x))

        ds = self.datastructure
        precision = self.float_precision

        tags_formatter = {"force": force_format,
                          "length": length_format,
                          "force-length": force_length_format}

        if text_tag not in tags_formatter:
            return None

        text_labels = {}
        formatter = tags_formatter[text_tag]

        for edge in ds.edges():
            label = formatter(edge)
            text_labels[edge] = label

        return text_labels


if __name__ == "__main__":
    pass
