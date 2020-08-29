from math import copysign
from math import fabs

from compas.geometry import Point
from compas.geometry import Line

from compas.geometry import length_vector
from compas.geometry import scale_vector
from compas.geometry import normalize_vector
from compas.geometry import add_vectors

from compas.utilities import rgb_to_hex
from compas.utilities import iterable_like
from compas.utilities import normalize_values

from compas_viewers.objectviewer import ObjectViewer


class TopologyViewer(ObjectViewer):
    def __init__(self, topology, *args, **kwargs):
        """
        A viewer tailored to display topological stuff.
        """
        super(TopologyViewer, self).__init__(*args, **kwargs)

        self.topology = topology

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

        self.point_size = 10.0
        self.line_width = 5.0

    def add_nodes(self, size=None):
        """
        Adds topology's nodes to the viewer's scene.

        Parameters
        ----------
        size : ``float``, optional.
            A uniform size for the nodes visualization.
            `Viewer.point_size`` will be taken if size is ``None``.
            Defaults to ``None``.
        """
        topology = self.topology
        if not size:
            size = self.point_size

        for node in topology.nodes():
            x, y, z = topology.node_coordinates(node)
            point = Point(x, y, z)

            node_type = topology.node_type(node) or "default"
            color = self.node_colors[node_type]

            settings = {
                "vertices.size": size,
                "vertices.color": rgb_to_hex(color)
            }
            self.add(point, settings=settings)

    def add_edges(self, width=None):
        """
        Draws the edges.
    
        Parameters
        ----------
        width : ``float`` or ``tuple``, optional.
            A uniform width for the edges if a ``float`` is supplied.
            A linear size range if a (min, max)``tuple`` is input.
            ``Viewer.line_width`` will be applied uniformly if width is ``None``.
            Defaults to ``None``.
        """
        topology = self.topology
        edges = list(topology.edges())

        if isinstance(width, tuple):
            new_min, new_max = width
            widths = normalize_values([fabs(topology.edge_force(e)) for e in edges], new_min, new_max)
        else:
            if not width:
                width = self.line_width
            widths = iterable_like(edges, [width], width)

        for i, edge in enumerate(edges):
            start, end = topology.edge_coordinates(*edge)
            line = Line(start, end)

            sign = copysign(1, topology.edge_force(edge))
            width = widths[i]
            color = self.edge_state_colors[sign]

            settings = {
                "edges.width": width,
                "edges.color": rgb_to_hex(color)
            }

            self.add(line, settings=settings)

    def add_loads(self, scale=1.0, color=(102, 255, 51), width=5.0, tol=1e-3):
        """
        Adds scaled line representations of the loads to the scene.

        Parameters
        ----------
        scale : ``float``
            The uniform length of the load lines. Defaults to ``1.0``.
        color : ``tuple``
            The arrows' uniform color in rgb. Defaults to black, ``(102, 255, 51)``. 
        width : ``float``
            The arrows uniform display width. Defaults to ``5.0``.
        tol : ``float``
            The minimum force magnitude to draw. Defaults to ``1e-3``. 
        """
        topology = self.topology

        for node in topology.nodes():
            q_vec = topology.node_load(node)

            if length_vector(q_vec) < tol:
                continue

            pt = scale_vector(normalize_vector(q_vec), scale)
            end = topology.node_coordinates(node)
            start = add_vectors(end, pt)
            line = Line(start, end)

            settings = {}
            settings["edges.color"] = rgb_to_hex(color)
            settings["edges.width"] = width
            
            self.add(line, settings=settings)
        
    def add_points(self, points, size, color=(255, 153, 0)):
        """
        """
        settings = {
            "vertices.size": size,
            "vertices.color": rgb_to_hex(color)
        }

        for point in points:
            if not isinstance(point, Point):
                x, y, z = point
                point = Point(x, y, z)
            self.add(point, settings=settings)
    
    def add_lines(self):
        """
        """
        return
    
    def add_mesh(self):
        """
        """
        return
    
    def add_polyline(self):
        """
        """
        return


if __name__ == "__main__":
    pass
