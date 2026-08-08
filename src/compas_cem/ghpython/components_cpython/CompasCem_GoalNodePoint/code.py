# r: compas_cem>=0.9.0
"""
Pull the position of a node to a target point.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import Rhino

from compas_rhino.conversions import point_to_compas

from compas_cem.optimization import PointGoal


class PointGoalComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        node_key: int | None,
        point: Rhino.Geometry.Point3d | None,
        weight: float | None,
    ) -> Any:
        weight = weight or 1.0

        if node_key is None or not point:
            return

        return PointGoal(node_key, point_to_compas(point), weight)
