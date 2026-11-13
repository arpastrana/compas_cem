# r: compas_cem>=0.10.0
"""
Shift the starting sequence of a selection of trails in a topology diagram, or align every trail so that as many deviation edges as possible are direct.
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
        auto_align: bool | None,
    ) -> Any:
        if not topology:
            return

        warning = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
        has_shifts = bool(origin_node_keys) or bool(sequences)

        if auto_align and has_shifts:
            message = "Turn auto_align on or connect origin_node_keys and sequences, not both."
            ghenv.Component.AddRuntimeMessage(warning, message)  # noqa: F821
            return

        if auto_align:
            topology = topology.copy()
            topology.align_trails()
            indirect_count = topology.number_of_indirect_deviation_edges()
            if indirect_count:
                template = (
                    "{} deviation edges stay indirect: no shift makes them direct."
                )
                message = template.format(indirect_count)
                ghenv.Component.AddRuntimeMessage(warning, message)  # noqa: F821
            return topology

        if not origin_node_keys or not sequences:
            message = "Connect origin_node_keys and sequences, or turn auto_align on."
            ghenv.Component.AddRuntimeMessage(warning, message)  # noqa: F821
            return

        topology = topology.copy()
        targets = iterable_like(origin_node_keys, sequences, sequences[-1])

        for node_key, sequence in zip(origin_node_keys, targets):
            topology.shift_trail(node_key, sequence)

        return topology
