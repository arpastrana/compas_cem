# r: compas_cem>=0.9.0
"""
Assemble a topology diagram.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import System

from compas_cem.diagrams import TopologyDiagram


class AssembleTopologyDiagramComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        trail_edges: System.Collections.Generic.List[object],
        deviation_edges: System.Collections.Generic.List[object],
        loads: System.Collections.Generic.List[object],
        supports: System.Collections.Generic.List[object],
        add_auxiliary_trails: bool | None,
    ) -> Any:
        add_auxiliary_trails = add_auxiliary_trails or False
        topology = TopologyDiagram()

        for trail_edge in trail_edges or []:
            if trail_edge:
                topology.add_edge(trail_edge)

        for deviation_edge in deviation_edges or []:
            if deviation_edge:
                topology.add_edge(deviation_edge)

        for load in loads or []:
            if load:
                topology.add_load(load)

        for support in supports or []:
            if support:
                topology.add_support(support)

        if trail_edges and supports:
            topology.build_trails(add_auxiliary_trails)

        elif deviation_edges and add_auxiliary_trails:
            topology.build_trails(add_auxiliary_trails)

        return topology
