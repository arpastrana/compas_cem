"""
Disassemble a topology diagram into its constituent parts.
"""
from ghpythonlib.componentbase import executingcomponent as component


class TopologyDisassemblyComponent(component):
    def RunScript(self, topology):
        if topology:
            trails = list(topology.trails())
            auxiliary_trails = list(topology.auxiliary_trails())

            edges = list(topology.edges())
            trail_edges = list(topology.trail_edges())
            deviation_edges = list(topology.deviation_edges())

            nodes = list(topology.nodes())
            origin_nodes = list(topology.origin_nodes())
            support_nodes = list(topology.support_nodes())

            return nodes, origin_nodes, support_nodes, edges, trail_edges, deviation_edges, trails, auxiliary_trails
