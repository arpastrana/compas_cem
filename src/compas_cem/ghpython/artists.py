from math import fabs

from compas.geometry import add_vectors
from compas.geometry import length_vector
from compas.geometry import scale_vector
from compas.geometry import normalize_vector
from compas.geometry import translate_points

from compas_ghpython import draw_points
from compas_ghpython import draw_lines
from compas_ghpython import draw_polylines

from compas_ghpython.artists import NetworkArtist

from compas_cem import COLORS


__all__ = ["FormArtist", "TopologyArtist"]


# ------------------------------------------------------------------------------
# Diagram artist
# ------------------------------------------------------------------------------


class DiagramArtist(NetworkArtist):
    """
    An artist to draw diagrams.

    Parameters
    ----------
    diagram : :class:`compas_cem.diagrams.Diagram`
        A diagram.
    args : list, optional
        Additional arguments for :class:`compas_ghpython.NetworkArtist`
    kwargs : dict, optional
        Extra named arguments for :class:`compas_ghpython.NetworkArtist`
    """
    def __init__(self, diagram, *args, **kwargs):
        super(DiagramArtist, self).__init__(diagram, *args, **kwargs)

        self.edge_state_colors = {-1: COLORS["compression"],
                                  1: COLORS["tension"],
                                  0: COLORS["edge"]}

        self.float_precision = "3f"
        self._diagram = diagram

    @property
    def diagram(self):
        """
        The diagram to draw.

        Returns
        -------
        form : :class:`compas_cem.diagrams.Diagram`
            A form diagram.
        """
        return self._diagram

    @diagram.setter
    def diagram(self, diagram):
        self._diagram = diagram

    def draw_nodes(self, nodes=None):
        """
        Draw a selection of nodes.

        Parameters
        ----------
        nodes: list, optional
            The selection of nodes that should be drawn.
            Default is ``None``, in which case all nodes are drawn.

        Returns
        -------
        nodes : list of :class:`Rhino.Geometry.Point3d`
        """
        nodes = nodes or list(self.diagram.nodes())
        points = []
        for node in nodes:
            points.append({'pos': self.diagram.node_coordinates(node)})

        return draw_points(points)

    def draw_edges(self, edges=None):
        """
        Draw a selection of edges.

        Parameters
        ----------
        edges : list, optional
            A list of edges to draw.
            The default is ``None``, in which case all edges are drawn.
        Returns
        -------
        edges: list of :class:`Rhino.Geometry.Line`
        """
        edges = edges or list(self.diagram.edges())
        lines = []
        for edge in edges:
            start, end = self.diagram.edge_coordinates(*edge)
            lines.append({'start': start, 'end': end})

        return draw_lines(lines)

    def draw_loads(self, nodes=None, scale=1.0, gap=0.0, min_load=1e-3):
        """
        Draw the loads applied to a selection of nodes.

        Parameters
        ----------
        nodes: list, optional
            A list of nodes to draw the loads upon.
            The default is ``None``, in which case all nodes are considered.
        scale : ``float``
            The scale of the loads.
            Defaults to ``1.0``.
        gap : ``float``
            The offset between a node and the incident load.
            Defaults to ``0.0``.
        min_load: ``float``
            The smallest load magnitude to draw.
            Defaults to ``1e-3``

        Returns
        -------
        loads : list of :class:`Rhino.Geometry.Line`
        """
        nodes = nodes or list(self.diagram.nodes())
        attrs = ["qx", "qy", "qz"]
        shift = {node: False for node in nodes}

        return self._draw_forces(nodes, attrs, scale, shift, gap, min_load)

    def _draw_forces(self, nodes, attrs, scale, shift, gap, tol):
        """
        Base method to draws forces (residuals or loads) on nodes as lines.

        Parameters
        ----------
        nodes: ``list``
            The list of node keys where to draw forces.
        attrs : ``list``
            The attribute names of the force vector to draw.
        scale : ``float``
            The forces scale factor.
        shift : ``bool``
            A flat to shift an arrow one length along its own axis.
        gap : ``float``
            The offset between the node and the force.
        tol : ``float``
            The minimum force magnitude to draw.

        Returns
        -------
        list of :class:`Rhino.Geometry.Line`
        """
        arrows = []

        for node in nodes:
            q_vec = self.diagram.node_attributes(node, attrs)
            q_vec_scaled = scale_vector(q_vec, scale)
            q_vec_norm = normalize_vector(q_vec)
            q_len = length_vector(q_vec)

            if q_len < tol:
                continue

            arrow = {}
            start = self.diagram.node_xyz(node)
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

            arrows.append(arrow)

        return draw_lines(arrows)

    def draw_nodes_support(self, nodes=None):
        """
        Draw a selection of the support nodes in the diagram.

        Parameters
        ----------
        nodes: list, optional
            The selection of support nodes that should be drawn.
            Default is ``None``, in which case all support nodes are drawn.

        Returns
        -------
        nodes : list of :class:`Rhino.Geometry.Point3d`
        """
        nodes = self._collection_keys("support_nodes", "is_node_support", nodes)
        return self.draw_nodes(nodes)

    def _collection_keys(self, iterator_func, filter_func, keys=None):
        """
        Safe choose the keys to draw a particular set of topological objects.

        Parameters
        ----------
        iterator_func : str
            The name of the diagram method that iterats over the objects.
        filter_func : str
            The name of the diagram method to check if a key is an object key.
        keys : list, optional
            The selection of the keys of the objects to draw.

        Returns
        -------
        keys : list of keys
        """
        if keys is None:
            iterator = getattr(self.diagram, iterator_func)
            keys = list(iterator())
        else:
            filterer = getattr(self.diagram, filter_func)
            keys = [key for key in keys if filterer(key)]
        return keys

    def clear_edges(self):
        """
        GH Artists are state-less. Therefore, clear does not have any effect.
        """
        pass

    def clear_nodes(self):
        """
        GH Artists are state-less. Therefore, clear does not have any effect.
        """
        pass

# ------------------------------------------------------------------------------
# Form diagram artist
# ------------------------------------------------------------------------------


class FormArtist(DiagramArtist):
    """
    Draw a form diagram with flair.

    Parameters
    ----------
    form_diagram : :class:`compas_cem.diagrams.FormDiagram`
        A form diagram.
    args : list, optional
        Additional arguments for :class:`compas_ghpython.NetworkArtist`
    kwargs : dict, optional
        Extra named arguments for :class:`compas_ghpython.NetworkArtist`
    """
    def __init__(self, form_diagram, *args, **kwargs):
        super(FormArtist, self).__init__(form_diagram, *args, **kwargs)

    def draw_reactions(self, nodes=None, scale=1.0, gap=0.0, min_force=1e-3):
        """
        Draw the reaction forces at a selection of support nodes.

        Parameters
        ----------
        nodes: list, optional
            A list of supports nodes to draw the reaction forces on.
            The default is ``None``, in which case all support nodes are taken.
        scale : ``float``
            The scale of the reaction forces.
            Defaults to ``1.0``.
        gap : ``float``
            The offset between a node and the incident reaction force.
            Defaults to ``0.0``.
        min_load: ``float``
            The smallest reaction force magnitude to draw.
            Defaults to ``1e-3``

        Returns
        -------
        reaction : list of :class:`Rhino.Geometry.Line`
        """
        diagram = self.diagram
        nodes = nodes or list(self.diagram.support_nodes())
        attrs = ["rx", "ry", "rz"]

        # TODO: needs a more robust check for arrow orientation
        # what we need is to know whether the arrow needs a full shift.
        shift = {}
        for node in nodes:
            if not diagram.is_node_support(node):
                continue
            s = False
            forces = [diagram.edge_force(e) for e in diagram.connected_edges(node)]
            max_force = max(forces, key=lambda f: fabs(f))
            if max_force < 0.0:
                s = True
            shift[node] = s

        return self._draw_forces(nodes, attrs, scale, shift, gap, min_force)

# ------------------------------------------------------------------------------
# Topology diagram artist
# ------------------------------------------------------------------------------


class TopologyArtist(DiagramArtist):
    """
    Draw a topology diagram with style.

    Parameters
    ----------
    topology_diagram : :class:`compas_cem.diagrams.TopologyDiagram`
        A topology diagram.
    args : list, optional
        Additional arguments for :class:`compas_ghpython.NetworkArtist`
    kwargs : dict, optional
        Extra named arguments for :class:`compas_ghpython.NetworkArtist`
    """
    def __init__(self, topology_diagram, *args, **kwargs):
        super(TopologyArtist, self).__init__(topology_diagram, *args, **kwargs)

    def draw_nodes_origin(self, nodes=None):
        """
        Draw a selection of the origin nodes in the topology diagram.

        Parameters
        ----------
        nodes: list, optional
            The selection of origin nodes that should be drawn.
            Default is ``None``, in which case all origin nodes are drawn.

        Returns
        -------
        rhino_nodes : list of :class:`Rhino.Geometry.Point3d`
        """
        if nodes is None:
            nodes = list(self.diagram.origin_nodes())
        else:
            nodes = [no for no in nodes if self.diagram.is_node_origin(no)]
        if not len(nodes) == 0:
            return self.draw_nodes(nodes)

    def draw_edges_deviation(self, edges=None):
        """
        Draw a selection of deviation edges.

        Parameters
        ----------
        edges : list, optional
            A list of deviation edges to draw.
            The default is ``None``, in which case all deviation edges are drawn.
        Returns
        -------
        rhino_edges : list of :class:`Rhino.Geometry.Line`
        """

        edges = self._collection_keys("deviation_edges", "is_deviation_edge", edges)
        if not len(edges) == 0:
            return self.draw_edges(edges)

    def draw_edges_trail(self, edges=None):
        """
        Draw a selection of trail edges.

        Parameters
        ----------
        edges : list, optional
            A list of trail edges to draw.
            The default is ``None``, in which case all trail edges are drawn.
        Returns
        -------
        rhino_edges : list of :class:`Rhino.Geometry.Line`
        """
        edges = self._collection_keys("trail_edges", "is_trail_edge", edges)
        if not len(edges) == 0:
            return self.draw_edges(edges)

    def draw_trails(self):
        """
        Draw the trails as Rhino polylines.

        Returns
        -------
        rhino_polylines : list of :class:`Rhino.Geometry.Polyline`
        """
        polylines = []
        for trail in self.diagram.trails():
            p = {}
            p["points"] = [self.diagram.node_xyz(node) for node in trail]
            polylines.append(p)

        return draw_polylines(polylines)
