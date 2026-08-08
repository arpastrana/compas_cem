# r: compas_cem>=0.9.0
"""
Shift the starting sequence of a selection of trails in a topology diagram.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import System

from compas.itertools import iterable_like


class ShiftTrailsSequenceComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        topology: Any,
        origin_node_keys: System.Collections.Generic.List[int],
        sequences: System.Collections.Generic.List[int],
    ) -> Any:
        if not topology or not origin_node_keys or not sequences:
            return

        topology = topology.copy()
        targets = iterable_like(origin_node_keys, sequences, sequences[-1])

        for node_key, sequence in zip(origin_node_keys, targets):
            topology.shift_trail(node_key, sequence)

        return topology
