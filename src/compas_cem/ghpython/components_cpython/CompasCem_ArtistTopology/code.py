# r: compas_cem>=0.9.0
"""
Draw a topology diagram.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import System

from compas_cem.ghpython import TopologyDiagramObject


class TopologyArtistComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        topology: Any,
        node_keys: System.Collections.Generic.List[int],
        edge_keys: System.Collections.Generic.List[object],
        force_min: float | None,
        force_scale: float | None,
    ) -> Any:
        node_keys = node_keys or None
        edge_keys = edge_keys or None
        force_min = force_min or 1e-3
        force_scale = force_scale or 1.0

        if not topology:
            return

        obj = TopologyDiagramObject(topology)

        nodes = obj.draw_nodes(node_keys)
        origin_nodes = obj.draw_nodes_origin(node_keys)
        support_nodes = obj.draw_nodes_support(node_keys)

        edges = obj.draw_edges(edge_keys)
        trail_edges = obj.draw_edges_trail(edge_keys)
        deviation_edges = obj.draw_edges_deviation(edge_keys)

        trails = obj.draw_trails()

        loads = obj.draw_loads(node_keys, min_load=force_min, scale=force_scale)

        return (
            nodes,
            origin_nodes,
            support_nodes,
            edges,
            trail_edges,
            deviation_edges,
            trails,
            loads,
        )
