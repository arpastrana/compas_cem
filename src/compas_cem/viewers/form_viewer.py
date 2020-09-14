from math import copysign
from math import fabs

from compas.geometry import Point
from compas.geometry import Line

from compas.geometry import length_vector
from compas.geometry import scale_vector
from compas.geometry import add_vectors

from compas.utilities import rgb_to_hex
from compas.utilities import iterable_like
from compas.utilities import normalize_values

from compas_viewers.objectviewer import ObjectViewer


class FormViewer(ObjectViewer):
    def __init__(self, form, *args, **kwargs):
        """
        A viewer tailored to display topological stuff.
        """
        super(FormViewer, self).__init__(*args, **kwargs)

        self.form = form

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
        Adds form's nodes to the viewer's scene.

        Parameters
        ----------
        size : ``float``, optional.
            A uniform size for the nodes visualization.
            `Viewer.point_size`` will be taken if size is ``None``.
            Defaults to ``None``.
        """
        form = self.form
        if not size:
            size = self.point_size

        for node in form.nodes():
            x, y, z = form.node_xyz(node) 
            point = Point(x, y, z)

            node_type = form.node_attribute(key=node, name="type") or "default"
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
        form = self.form
        edges = list(form.edges())

        if isinstance(width, tuple):
            new_min, new_max = width
            widths = normalize_values([fabs(form.edge_force(e)) for e in edges], new_min, new_max)
        else:
            if not width:
                width = self.line_width
            widths = iterable_like(edges, [width], width)

        for i, edge in enumerate(edges):
            start, end = form.edge_coordinates(*edge)
            line = Line(start, end)

            sign = copysign(1, form.edge_force(edge))
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
            The scale of the load lines. Defaults to ``1.0``.
        color : ``tuple``
            The arrows' uniform color in rgb. Defaults to ``(102, 255, 51)``. 
        width : ``float``
            The arrows uniform display width. Defaults to ``5.0``.
        tol : ``float``
            The minimum force magnitude to draw. Defaults to ``1e-3``. 
        """
        attr = "node_load"
        self._add_forces(attr, scale, color, width, tol)

    def add_residuals(self, scale=1.0, color=(0, 204, 255), width=5.0, tol=1e-3):
        """
        Adds scaled line representations of the node residual forces.

        Parameters
        ----------
        scale : ``float``
            The scale of the residual force lines. Defaults to ``1.0``.
        color : ``tuple``
            The arrows' uniform color in rgb. Defaults to ``(0, 204, 255)``. 
        width : ``float``
            The arrows uniform display width. Defaults to ``5.0``.
        tol : ``float``
            The minimum force magnitude to draw. Defaults to ``1e-3``. 
        """
        attr = "node_residual"
        self._add_forces(attr, scale, color, width, tol)


    def _add_forces(self, attr, scale, color, width, tol):
        """
        Adds scaled line representations of forces to the scene.

        Parameters
        ----------
        attr : ``str``
            The node attribute to add to the scene.
        scale : ``float``
            The line scale.
        color : ``tuple``
            The line color in rgb.
        width : ``float``
            The line display width.
        tol : ``float``
            The smallest line length to draw.
        """
        form = self.form

        for node in form.nodes():
            function = getattr(form, attr)
            q_vec = function(node)

            if length_vector(q_vec) < tol:
                continue

            pt = scale_vector(q_vec, -scale)
            end = form.node_xyz(node)
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
    
    def add_mesh(
        self,
        mesh,
        color=(50, 50, 50),
        edges_color=(150, 150, 150),
        edges_width = 5.0,
        vertices_size = 0.5,
        opacity=0.7,
        vertices_on=False,
        edges_on=True,
        faces_on=True
        ):
        """
        """
        settings = {
        'color': rgb_to_hex(color),
        'edges.color': rgb_to_hex(edges_color),
        'edges.width': edges_width,
        'opacity': opacity,
        'vertices.size': vertices_size,
        'vertices.on': vertices_on,
        'edges.on': edges_on,
        'faces.on': faces_on
        }
        self.add(mesh, settings=settings)

    def add_lines(self):
        """
        """
        raise NotImplementedError
        
    def add_polyline(self):
        """
        """
        raise NotImplementedError


if __name__ == "__main__":
    pass
