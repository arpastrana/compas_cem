"""
Disassemble a topology diagram into its constituent parts.
"""
from ghpythonlib.componentbase import executingcomponent as component


class TopologyDisassemblyComponent(component):
    def RunScript(self, topology):
        if not topology:
            return

        trail_keys = list(topology.trails())
        auxiliary_trail_keys = list(topology.auxiliary_trails())

        edge_keys = list(topology.edges())
        trail_edge_keys = list(topology.trail_edges())
        deviation_edge_keys = list(topology.deviation_edges())

        node_keys = list(topology.nodes())
        origin_node_keys = list(topology.origin_nodes())
        support_node_keys = list(topology.support_nodes())

        return node_keys, origin_node_keys, support_node_keys, edge_keys, trail_edge_keys, deviation_edge_keys, trail_keys, auxiliary_trail_keys
