def topology_equilibrium(topology_diagram, *args, **kwargs):
    """
    """
    for sequence in topology_diagram.vertex_sequences():
        for vertex in sequence:
            vertex_equilibrium(topology_diagram, vertex)


def vertex_equilibrium(topology, vertex):
    """
    """
    for edge in topology.vertex_connected_edges(vertex):
        edge_type = topology.edge_attribute(edge, "type")
        
        trail_edges = []
        direct_dev_edges = []
        indirect_dev_edges = []

    return

if __name__ == "__main__":
    pass