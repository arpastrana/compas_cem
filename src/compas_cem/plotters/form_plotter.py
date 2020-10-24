from math import copysign

from functools import partial

from compas.geometry import add_vectors
from compas.geometry import length_vector
from compas.geometry import scale_vector

from compas.utilities import geometric_key

from compas_plotters import NetworkPlotter


class FormPlotter(NetworkPlotter):
    """
    A plotter tailored to draw form-related matters.
    
    Parameters
    ----------
    form_diagram : :class:`compas_cem.diagrams.FormDiagram`
        The form diagram to plot.

    Example
    -------
    
    :include-source:

    import os
    from compas_cem import JSON_DATA
    from compas_cem.diagrams import FormDiagram
    from compas_cem.plotters import FormPlotter

    IN = os.path.abspath(os.path.join(JSON_DATA, "w1_cem_2d_bridge_rhino.json"))
    form = FormDiagram.from_json(IN)

    plotter = FormPlotter(form)
    plotter.draw_nodes(radius=0.30, text="key")
    plotter.draw_edges(text="force")
    plotter.draw_loads(scale=-2.0)
    plotter.draw_residuals(scale=-0.25)

    plotter.show()

    """

    def __init__(self, form_diagram, *args, **kwargs):
        super(FormPlotter, self).__init__(form_diagram, *args, **kwargs)
        
        self._node_colors = {
            "support": (0, 153, 0),  # green
            "root": (153, 102, 255),  # root
            "default": (150, 150, 150)  # gray
            }

        self._edge_colors = {
            "trail": (255, 0, 255),
            "deviation": (0, 255, 0)
            }

        self._edge_state_colors = {
            -1: (0, 0, 255),
            1: (255, 0, 0),
            0: (0, 0, 0)
            }

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
    def node_colors(self):
        """
        The default colors to draw the nodes of a form diagram.

        Returns
        -------
        node_colors : ``dict`` of ``color``
            For supports, green (0, 153, 0).
            For root nodes, cyan (153, 102, 255).
            Otherwise, gray (150, 150, 150).
        """
        return self._node_colors

    @property
    def edge_colors(self):
        """
        The default colors to draw the edges of a form diagram.

        Returns
        -------
        edge_colors : ``dict`` of ``color``
            For trail edges, magenta (255, 0, 155).
            For deviation edges, green (0, 255, 0).
        """
        return self._edge_colors

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
        precision: ``str``
            The float precision value. Defaults to ``3f``.
        """
        return self._float_precision

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
        cmap = self.node_colors
        ds = self.datastructure
        cmap["d"] = (255, 255, 255)
        nc = {n: cmap[attr.get("type", "d")] for n, attr in ds.nodes(True)}

        text = kwargs.get("text")
        if text and text != "key":
            kwargs["text"] = self._text_labels_nodes(text)

        super(FormPlotter, self).draw_nodes(facecolor=nc, *args, **kwargs)

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
        cmap = self.edge_state_colors
        ds = self.datastructure
        ec = {e: cmap[copysign(1.0, attr.get("force", 0.0))] for e, attr in ds.edges(True)}

        text = kwargs.get("text")
        if text and text != "key":
            kwargs["text"] = self._text_labels_edges(text)

        super(FormPlotter, self).draw_edges(color=ec, *args, **kwargs)

    def draw_loads(self, keys=None, scale=1.0, color=(102, 255, 51), width=2.0, tol=1e-3):
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
        color : ``tuple``
            The arrows' uniform color in rgb. Defaults to ``(102, 255, 51)``. 
        width : ``float``
            The arrows uniform display width. Defaults to ``4.0``.
        tol : ``float``
            The minimum force magnitude to draw. Defaults to ``1e-3``. 
        """
        if not keys:
            keys = list(self.datastructure.nodes())
        attrs = ["qx", "qy", "qz"]
        self._draw_forces(keys, attrs, scale, color, width, tol)

    def draw_residuals(self, keys=None, scale=1.0, color=(0, 204, 255), width=3.0, tol=1e-3):
        """
        Draws the node residual forces in a ``FormDiagram`` as scaled arrows.

        Parameters
        ----------
        keys : ``list``
            The list of node keys where to draw forces. 
            If nodes is ``None``, all nodes in will be considered.
            Defaults to ``None``.
        scale : ``float``
            The scale of the residual arrows. Defaults to ``1.0``.
        color : ``tuple``
            The arrows' uniform color in rgb. Defaults to ``(0, 204, 255)``. 
        width : ``float``
            The arrows uniform display width. Defaults to ``3.0``.
        tol : ``float``
            The minimum force magnitude to draw. Defaults to ``1e-3``. 
        """
        if not keys:
            keys = list(self.datastructure.nodes())
        attrs = ["rx", "ry", "rz"]
        self._draw_forces(keys, attrs, scale, color, width, tol)

    def _draw_forces(self, keys, attrs, scale, color, width, tol):
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
        tol : ``float``
            The minimum force magnitude to draw.
        """
        ds = self.datastructure
        arrows = []

        for node in ds.nodes():
            q_vec = ds.node_attributes(node, attrs)
            
            if length_vector(q_vec) < tol:
                continue

            arrow = {}
            arrow["start"] = ds.node_xyz(node)
            pt = scale_vector(q_vec, -scale)
            arrow["end"] = add_vectors(arrow["start"], pt)
            arrow["color"] = color
            arrow["width"] = width
            
            arrows.append(arrow)
        
        super(FormPlotter, self).draw_arrows(arrows)

    def draw_segments(self, segments, color=(40, 40, 40), width=0.5):
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

        super(FormPlotter, self).draw_lines(lines)
    
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
        ds = self.datastructure
        precision = self.float_precision
        gkey_format = lambda x: geometric_key(ds.node_xyz(x), precision)
        key_gkey_format = lambda x: "{} / {}".format(x, gkey_format(x))

        tags_formatter = {
            "xyz": gkey_format,
            "key-xyz": key_gkey_format
            }

        if text_tag not in tags_formatter:
            return

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
        ds = self.datastructure
        force_format = partial(ds.edge_attribute, name="force")
        length_format = partial(ds.edge_attribute, name="length")

        def parameter_format(key):
            if ds.is_trail_edge(key):
                return length_format(key)
            elif ds.is_deviation_edge(key):
                return force_format(key)

        tags_formatter = {
            "force": force_format,
            "length": length_format,
            "force-length": parameter_format
            }

        if text_tag not in tags_formatter:
            return

        precision = self.float_precision
        text_labels = {}
        formatter = tags_formatter[text_tag]

        for edge in ds.edges():
            label = formatter(key=edge)
            text_labels[edge] = "{0:.{1}}".format(label, precision)
        
        return text_labels

if __name__ == "__main__":
    pass