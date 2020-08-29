from math import copysign

from functools import partial

from compas.geometry import add_vectors
from compas.geometry import length_vector
from compas.geometry import normalize_vector
from compas.geometry import scale_vector

from compas.utilities import geometric_key

from compas_plotters import NetworkPlotter


class TopologyPlotter(NetworkPlotter):
    def __init__(self, *args, **kwargs):
        """
        A plotter tailored to draw topology-related matters.
        """
        super(TopologyPlotter, self).__init__(*args, **kwargs)
        
        self.node_colors = {
            "support": (0, 153, 0),  # green
            "root": (153, 102, 255),  # root
            "default": (150, 150, 150)  # gray
            }

        self.edge_colors = {
            "trail": (255, 0, 255),
            "deviation": (0, 255, 0)
            }

        self.edge_state_colors = {
            -1: (0, 0, 255),
            1: (255, 0, 0),
            0: (0, 0, 0)
            }

        self.float_precision = "3f"

    def draw_nodes(self, *args, **kwargs):
        """
        Draws the nodes.

        Parameters
        ----------
        *args : ``list``
            Additional plotter arguments
        **kwargs : ``dict``
            Additional plotter keyword arguments
        """
        cmap = self.node_colors
        ds = self.datastructure
        cmap["d"] = (255, 255, 255)
        nc = {n: cmap[attr.get("type", "d")] for n, attr in ds.nodes(True)}

        text = kwargs.get("text")
        if text and text != "key":
            kwargs["text"] = self._text_labels_nodes(text)

        super(TopologyPlotter, self).draw_nodes(facecolor=nc, *args, **kwargs)

    def draw_edges(self, *args, **kwargs):
        """
        Draws the edges.
    
        Parameters
        ----------
        *args : ``list``
            Additional plotter arguments
        **kwargs : ``dict``
            Additional plotter keyword arguments
        """
        cmap = self.edge_state_colors
        ds = self.datastructure
        ec = {e: cmap[copysign(1.0, attr.get("force", 0.0))] for e, attr in ds.edges(True)}

        text = kwargs.get("text")
        if text and text != "key":
            kwargs["text"] = self._text_labels_edges(text)

        super(TopologyPlotter, self).draw_edges(color=ec, *args, **kwargs)

    def draw_loads(self, scale=0.5, color=(0, 0, 0), width=4.0, tol=1e-3):
        """
        Draws scaled arrow representations of the loads.

        Parameters
        ----------
        scale : ``float``
            The uniform length of the load arrows. Defaults to ``0.5``.
        color : ``tuple``
            The arrows' uniform color in rgb. Defaults to black, ``(0, 0, 0)``. 
        width : ``float``
            The arrows uniform display width. Defaults to ``4.0``.
        tol : ``float``
            The minimum force magnitude to draw. Defaults to ``1e-3``. 
        """
        ds = self.datastructure
        arrows = []

        for node, attr in ds.nodes(True):
            q_vec = ds.node_attributes(node, ["qx", "qy", "qz"])
            if length_vector(q_vec) < tol:
                continue

            arrow = {}
            arrow["end"] = ds.node_coordinates(node)
            pt = scale_vector(normalize_vector(q_vec), -scale)
            arrow["start"] = add_vectors(arrow["end"], pt)
            arrow["color"] = color
            arrow["width"] = width
            
            arrows.append(arrow)
        
        super(TopologyPlotter, self).draw_arrows(arrows)

    def draw_segments(self, segments, color=(40, 40, 40), width=0.5):
        """
        Draws lines.

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

        super(TopologyPlotter, self).draw_lines(lines)
    
    def _text_labels_nodes(self, text_tag):
        """
        Generates text labels to plot on nodes based on a tag query.

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
        gkey_format = lambda x: geometric_key(ds.node_coordinates(x), precision)
        key_gkey_format = lambda x: "{} / {}".format(x, gkey_format(x))

        tags_formatter = {
            "xyz": gkey_format,
            "key/xyz": key_gkey_format
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
        Generates text labels to plot on edges based on a tag query.

        Input
        -----
        text_tag : `str`
            Tag query. Supported tags are: "attr", "force" and "length".
        
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
            "parameter": parameter_format
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