# r: compas_cem>=0.9.0
"""
Make the reaction force on a trail edge to meet a target force vector.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import Rhino

from compas_rhino.conversions import vector_to_compas

from compas_cem.optimization import ReactionForceGoal


class ReactionForceGoalComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        node_key: int | None,
        vector: Rhino.Geometry.Vector3d | None,
        weight: float | None,
    ) -> Any:
        weight = weight or 1.0

        if node_key is None or not vector:
            return

        return ReactionForceGoal(node_key, vector_to_compas(vector), weight)
