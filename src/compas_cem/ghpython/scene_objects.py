from math import fabs

from compas.geometry import add_vectors
from compas.geometry import length_vector
from compas.geometry import normalize_vector
from compas.geometry import scale_vector
from compas.geometry import translate_points
from compas.scene import register
from compas_ghpython.scene import GraphObject
from compas_rhino.conversions import line_to_rhino
from compas_rhino.conversions import point_to_rhino
from compas_rhino.conversions import polyline_to_rhino_curve

from compas_cem.diagrams import FormDiagram
from compas_cem.diagrams import TopologyDiagram

__all__ = [
    "DiagramObject",
    "FormDiagramObject",
    "TopologyDiagramObject",
    "register_ghpython_scene_objects",
]


class DiagramObject(GraphObject):
    """
    A scene object that draws a diagram in Grasshopper.

    Notes
    -----
    Every draw method takes an explicit selection, because the Grasshopper
    components expose the selection as a component input. Drawing returns bare
    Rhino geometry and carries no color, so the coloring is left to whatever
    consumes the geometry downstream.

    Node positions are read from the scene object rather than from the diagram,
    so a transformation set on the object applies to everything it draws.
    """

    @property
    def diagram(self):
        """
        The diagram this object draws.
        """
        return self.graph

    # ==========================================================================
    # Draw
    # ==========================================================================

    def draw_nodes(self, nodes=None):
        """
        Draw a selection of nodes.

        Parameters
        ----------
        nodes :
            The nodes to draw. If `None`, every node is drawn.

        Returns
        -------
        points :
            One Rhino point per drawn node.
        """
        nodes = self.diagram.nodes() if nodes is None else nodes
        node_xyz = self.node_xyz

        return [point_to_rhino(node_xyz[node]) for node in nodes]

    def draw_edges(self, edges=None):
        """
        Draw a selection of edges.

        Parameters
        ----------
        edges :
            The edges to draw. If `None`, every edge is drawn.

        Returns
        -------
        lines :
            One Rhino line per drawn edge.
        """
        edges = self.diagram.edges() if edges is None else edges
        node_xyz = self.node_xyz

        return [line_to_rhino((node_xyz[u], node_xyz[v])) for u, v in edges]

    def draw_nodes_support(self, nodes=None):
        """
        Draw a selection of the support nodes of the diagram.

        Parameters
        ----------
        nodes :
            The nodes to draw, of which only the supports are kept. If `None`,
            every support node is drawn.

        Returns
        -------
        points :
            One Rhino point per drawn support node.
        """
        nodes = self._selected_keys("support_nodes", "is_node_support", nodes)

        return self.draw_nodes(nodes)

    def draw_loads(self, nodes=None, scale=1.0, gap=0.0, min_load=1e-3):
        """
        Draw the loads applied to a selection of nodes.

        Parameters
        ----------
        nodes :
            The nodes to draw the loads of. If `None`, every node is taken.
        scale :
            The factor to scale the load vectors by.
        gap :
            The offset between a node and the load drawn at it.
        min_load :
            The smallest load magnitude worth drawing.

        Returns
        -------
        lines :
            One Rhino line per drawn load.
        """
        nodes = list(self.diagram.nodes()) if nodes is None else list(nodes)
        shift = {node: False for node in nodes}

        return self._draw_forces(
            nodes=nodes,
            attr_names=["qx", "qy", "qz"],
            scale=scale,
            shift=shift,
            gap=gap,
            tol=min_load,
        )

    def _draw_forces(self, nodes, attr_names, scale, shift, gap, tol):
        """
        Draw forces at a selection of nodes as scaled lines.

        Parameters
        ----------
        nodes :
            The nodes to draw a force at.
        attr_names :
            The node attributes that hold the force vector.
        scale :
            The factor to scale the force vectors by.
        shift :
            A mapping of nodes to whether the force is shifted one length along
            its own axis.
        gap :
            The offset between a node and the force drawn at it.
        tol :
            The smallest force magnitude worth drawing.

        Returns
        -------
        lines :
            One Rhino line per drawn force.

        Notes
        -----
        The magnitude is tested before the vector is normalized, so a node
        carrying no force is skipped instead of dividing by a zero length.
        """
        diagram = self.diagram
        node_xyz = self.node_xyz

        lines = []
        for node in nodes:
            vector = diagram.node_attributes(node, attr_names)
            length = length_vector(vector)

            if length < tol:
                continue

            scaled = scale_vector(vector, scale)
            start = node_xyz[node]
            end = add_vectors(start, scaled)

            gap_force = gap
            if shift[node]:
                gap_force = (gap + length_vector(scaled)) * -1

            gap_vector = scale_vector(normalize_vector(vector), gap_force)
            start, end = translate_points([start, end], gap_vector)

            lines.append(line_to_rhino((start, end)))

        return lines

    # ==========================================================================
    # Selection
    # ==========================================================================

    def _selected_keys(self, iterator_name, filter_name, keys=None):
        """
        Narrow a selection down to one kind of topological object.

        Parameters
        ----------
        iterator_name :
            The name of the diagram method that iterates over the objects.
        filter_name :
            The name of the diagram method that tests a single key.
        keys :
            The selection to narrow. If `None`, every matching key is taken.

        Returns
        -------
        keys :
            The keys that name an object of the wanted kind.
        """
        if keys is None:
            iterator = getattr(self.diagram, iterator_name)
            return list(iterator())

        matches = getattr(self.diagram, filter_name)

        return [key for key in keys if matches(key)]


class FormDiagramObject(DiagramObject):
    """
    A scene object that draws a form diagram in Grasshopper.
    """

    @property
    def form(self):
        """
        The form diagram this object draws.
        """
        return self.graph

    def draw_reactions(self, nodes=None, scale=1.0, gap=0.0, min_force=1e-3):
        """
        Draw the reaction forces at a selection of support nodes.

        Parameters
        ----------
        nodes :
            The nodes to draw the reaction forces of. If `None`, every node is
            taken.
        scale :
            The factor to scale the reaction forces by.
        gap :
            The offset between a node and the reaction force drawn at it.
        min_force :
            The smallest reaction force magnitude worth drawing.

        Returns
        -------
        lines :
            One Rhino line per drawn reaction force.
        """
        nodes = list(self.form.nodes()) if nodes is None else list(nodes)

        return self._draw_forces(
            nodes=nodes,
            attr_names=["rx", "ry", "rz"],
            scale=scale,
            shift=self._reaction_shifts(nodes),
            gap=gap,
            tol=min_force,
        )

    def _reaction_shifts(self, nodes):
        """
        Whether the reaction force at every node points back into its trail.

        Parameters
        ----------
        nodes :
            The nodes to decide the shift of.

        Returns
        -------
        shifts :
            A mapping of nodes to whether the reaction force is shifted.

        Notes
        -----
        A reaction is shifted when the strongest edge meeting the node is in
        compression, so the force reads as pushing against the support rather
        than pulling away from it. A node with no connected edge is never
        shifted, which also keeps the strongest-edge search off an empty set.

        TODO: needs a more robust check for orientation. What is wanted is to
        know whether the force needs a full shift.
        """
        form = self.form

        shifts = {}
        for node in nodes:
            forces = [form.edge_force(e) for e in form.node_connected_edges(node)]
            if not forces:
                shifts[node] = False
                continue
            shifts[node] = max(forces, key=lambda f: fabs(f)) < 0.0

        return shifts


class TopologyDiagramObject(DiagramObject):
    """
    A scene object that draws a topology diagram in Grasshopper.
    """

    @property
    def topology(self):
        """
        The topology diagram this object draws.
        """
        return self.graph

    def draw_nodes_origin(self, nodes=None):
        """
        Draw a selection of the origin nodes of the topology diagram.

        Parameters
        ----------
        nodes :
            The nodes to draw, of which only the origins are kept. If `None`,
            every origin node is drawn.

        Returns
        -------
        points :
            One Rhino point per drawn origin node.
        """
        nodes = self._selected_keys("origin_nodes", "is_node_origin", nodes)

        return self.draw_nodes(nodes)

    def draw_edges_trail(self, edges=None):
        """
        Draw a selection of the trail edges of the topology diagram.

        Parameters
        ----------
        edges :
            The edges to draw, of which only the trails are kept. If `None`,
            every trail edge is drawn.

        Returns
        -------
        lines :
            One Rhino line per drawn trail edge.
        """
        edges = self._selected_keys("trail_edges", "is_trail_edge", edges)

        return self.draw_edges(edges)

    def draw_edges_deviation(self, edges=None):
        """
        Draw a selection of the deviation edges of the topology diagram.

        Parameters
        ----------
        edges :
            The edges to draw, of which only the deviations are kept. If
            `None`, every deviation edge is drawn.

        Returns
        -------
        lines :
            One Rhino line per drawn deviation edge.
        """
        edges = self._selected_keys("deviation_edges", "is_deviation_edge", edges)

        return self.draw_edges(edges)

    def draw_trails(self):
        """
        Draw the trails of the topology diagram.

        Returns
        -------
        curves :
            One Rhino polyline curve per trail.

        Notes
        -----
        A polyline curve is drawn rather than a polyline, because Grasshopper
        unpacks a bare polyline output into its points.
        """
        node_xyz = self.node_xyz

        curves = []
        for trail in self.topology.trails():
            points = [node_xyz[node] for node in trail]
            curves.append(polyline_to_rhino_curve(points))

        return curves


def register_ghpython_scene_objects():
    """
    Register the diagram scene objects with the Grasshopper context.
    """
    register(FormDiagram, FormDiagramObject, context="Grasshopper")
    register(TopologyDiagram, TopologyDiagramObject, context="Grasshopper")
