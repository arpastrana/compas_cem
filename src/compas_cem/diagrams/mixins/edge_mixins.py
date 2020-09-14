

__all__ = [
    "EdgeMixins"
]


# ==============================================================================
# Edge Mixin
# ==============================================================================

class EdgeMixins(object):
    """
    """
    def add_edge(self, edge):
        """
        Adds a either a deviation or a trail object as an edge.

        Parameters
        ----------
            edge_object : ``Edge``
                An edge element.

        Returns
        -------
            key : ``tuple``
                An edge key.
        """
        edge_keys = []
        # breakpoint()
        for node in edge:
            key = self.node_key(node)

            if key is not None:
                edge_keys.append(key)
                continue
            
            xyz = None
            if not isinstance(key, int):
                xyz = node
            
            key = self.add_node(key, xyz)
            edge_keys.append(key)

        u, v = edge_keys
        attr = {k: v for k, v in edge.attributes.items()}
        return super(EdgeMixins, self).add_edge(u=u, v=v, attr_dict=attr)

# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    from compas_cem.diagrams.form_diagram import FormDiagram
    from compas_cem.elements import DeviationEdge
    from compas.geometry import Line
    
    form = FormDiagram()
    form.add_node(xyz=[0.0, 1.0, 0.0])

    line = Line([0.0, 1.0, 0.0], [2.0, 0.0, 0.0])
    edge = form.add_edge(DeviationEdge.from_line(line, 10.0))

    assert edge == (0, 1), "{}".format(edge)
    assert form.node_xyz(0) == [0.0, 1.0, 0.0]
    assert form.node_xyz(1) == [2.0, 0.0, 0.0]
    assert form.edge_force(edge) == 10.0
    assert form.number_of_nodes() == 2
    assert form.number_of_edges() == 1
