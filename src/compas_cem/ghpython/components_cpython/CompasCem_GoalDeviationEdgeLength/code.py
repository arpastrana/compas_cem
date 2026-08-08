# r: compas_cem>=0.9.0
"""
Make the length of a deviation edge reach a target value.
"""

from __future__ import annotations

from typing import Any

import Grasshopper

from compas_cem.optimization import DeviationEdgeLengthGoal


class DeviationEdgeLengthGoalComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        edge_key: Any,
        length: float | None,
        weight: float | None,
    ) -> Any:
        weight = weight or 1.0

        if not edge_key or length is None:
            return

        return DeviationEdgeLengthGoal(edge_key, length, weight)
