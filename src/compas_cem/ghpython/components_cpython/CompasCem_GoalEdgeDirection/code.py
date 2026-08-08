# r: compas_cem>=0.9.0
"""
Align the direction of a trail or a deviation edge with a target vector.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import Rhino

from compas_rhino.conversions import vector_to_compas

from compas_cem.optimization import EdgeDirectionGoal


class EdgeDirectionGoalComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        edge_key: Any,
        vector: Rhino.Geometry.Vector3d | None,
        weight: float | None,
    ) -> Any:
        weight = weight or 1.0

        if not edge_key or not vector:
            return

        return EdgeDirectionGoal(edge_key, vector_to_compas(vector), weight)
