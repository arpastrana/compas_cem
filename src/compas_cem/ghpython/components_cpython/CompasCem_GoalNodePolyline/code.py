# r: compas_cem>=0.9.0
"""
Pull the position of a node to a target polyline.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import Rhino

from compas_rhino.conversions import polyline_to_compas

from compas_cem.optimization import PolylineGoal


class PolylineGoalComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        node_key: int | None,
        polyline: Rhino.Geometry.Polyline | None,
        weight: float | None,
    ) -> Any:
        weight = weight or 1.0

        if node_key is None or not polyline:
            return

        return PolylineGoal(node_key, polyline_to_compas(polyline), weight)
