from compas_cem.elements import Node


__all__ = [
    "EdgeMixins"
]

# ==============================================================================
# Edge Mixins
# ==============================================================================


class EdgeMixins(object):
    """
    """
    def add_edge(self, edge):
        """
        Adds a deviation or a trail edge.

        Parameters
        ----------
        edge : ``Edge``
            An edge element.

        Returns
        -------
        key : ``tuple``
            An edge key.
        """
        edge_keys = []

        for node in edge:
            key = self.node_key(node)

            if key is not None:
                edge_keys.append(key)
                continue

            xyz = None
            if not isinstance(key, int):
                xyz = node

            key = self.add_node(Node(key, xyz))
            edge_keys.append(key)

        u, v = edge_keys
        attr = {k: v for k, v in edge.attributes.items()}
        return super(EdgeMixins, self).add_edge(u=u, v=v, attr_dict=attr)

# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    from compas_cem.diagrams import TopologyDiagram
    from compas_cem.elements import DeviationEdge
    from compas.geometry import Line

    topology = TopologyDiagram()
    topology.add_node(Node.from_point([0.0, 1.0, 0.0]))

    line = Line([0.0, 1.0, 0.0], [2.0, 0.0, 0.0])
    edge = topology.add_edge(DeviationEdge.from_line(line, 10))

    assert edge == (0, 1), "{}".format(edge)
    assert topology.node_xyz(0) == [0.0, 1.0, 0.0]
    assert topology.node_xyz(1) == [2.0, 0.0, 0.0]
    assert topology.edge_force(edge) == 10.0
    assert topology.number_of_nodes() == 2
    assert topology.number_of_edges() == 1
