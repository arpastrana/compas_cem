"""
Build a topology diagram.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.diagrams import TopologyDiagram


class BuildTopologyDiagramComponent(component):
    def RunScript(self, nodes, trail_edges, deviation_edges, loads, supports):

        topology = TopologyDiagram()

        if nodes:
            for node in nodes:
                topology.add_node(node)

        if trail_edges:
            for trail_edge in trail_edges:
                topology.add_edge(trail_edge)

        if deviation_edges:
            for deviation_edge in deviation_edges:
                topology.add_edge(deviation_edge)

        if loads:
            for load in loads:
                topology.add_load(load)

        if supports:
            for support in supports:
                topology.add_support(support)

        return topology
