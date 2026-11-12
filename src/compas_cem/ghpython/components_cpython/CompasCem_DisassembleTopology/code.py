# r: compas_cem>=0.9.1
"""
Disassemble a topology diagram into its constituent parts.
"""

from __future__ import annotations

from typing import Any

import Grasshopper


class TopologyDisassemblyComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self, topology: Any, filter_auxiliary: bool | None) -> Any:
        if not topology:
            return

        auxiliary_nodes = set()
        auxiliary_edges = set()
        if filter_auxiliary:
            auxiliary_nodes = set(topology.auxiliary_support_nodes())
            auxiliary_edges = {tuple(edge) for edge in topology.auxiliary_trails()}

        sequence_keys = []
        for sequence in topology.sequences():
            sequence_nodes = tuple(
                node for node in sequence if node not in auxiliary_nodes
            )
            sequence_keys.append(sequence_nodes)

        trail_keys = [
            trail for trail in topology.trails() if auxiliary_nodes.isdisjoint(trail)
        ]
        auxiliary_trail_keys = []
        if not filter_auxiliary:
            auxiliary_trail_keys = list(topology.auxiliary_trails())

        edge_keys = [edge for edge in topology.edges() if edge not in auxiliary_edges]
        trail_edge_keys = [
            edge for edge in topology.trail_edges() if edge not in auxiliary_edges
        ]
        deviation_edge_keys = list(topology.deviation_edges())

        node_keys = [node for node in topology.nodes() if node not in auxiliary_nodes]
        origin_node_keys = list(topology.origin_nodes())
        support_node_keys = [
            node for node in topology.support_nodes() if node not in auxiliary_nodes
        ]

        return (
            node_keys,
            origin_node_keys,
            support_node_keys,
            edge_keys,
            trail_edge_keys,
            deviation_edge_keys,
            sequence_keys,
            trail_keys,
            auxiliary_trail_keys,
        )
