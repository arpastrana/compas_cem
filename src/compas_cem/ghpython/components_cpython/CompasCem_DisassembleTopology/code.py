# r: compas_cem>=0.9.0
"""
Disassemble a topology diagram into its constituent parts.
"""

from __future__ import annotations

from typing import Any

import Grasshopper


class TopologyDisassemblyComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self, topology: Any) -> Any:
        if not topology:
            return

        sequence_keys = list(topology.sequences())
        trail_keys = list(topology.trails())
        auxiliary_trail_keys = list(topology.auxiliary_trails())

        edge_keys = list(topology.edges())
        trail_edge_keys = list(topology.trail_edges())
        deviation_edge_keys = list(topology.deviation_edges())

        node_keys = list(topology.nodes())
        origin_node_keys = list(topology.origin_nodes())
        support_node_keys = list(topology.support_nodes())

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
