# r: compas_cem>=0.9.0
"""
Pull the position of a node to a target line ray.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import Rhino

from compas_rhino.conversions import line_to_compas

from compas_cem.optimization import LineGoal


class LineGoalComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        node_key: int | None,
        line: Rhino.Geometry.Line | None,
        weight: float | None,
    ) -> Any:
        weight = weight or 1.0

        if node_key is None or not line:
            return

        return LineGoal(node_key, line_to_compas(line), weight)
