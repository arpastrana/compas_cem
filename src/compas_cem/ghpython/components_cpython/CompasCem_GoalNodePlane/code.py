# r: compas_cem>=0.9.0
"""
Pull the position of a node to a target plane.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import Rhino

from compas_rhino.conversions import plane_to_compas

from compas_cem.optimization import PlaneGoal


class PlaneGoalComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        node_key: int | None,
        plane: Rhino.Geometry.Plane | None,
        weight: float | None,
    ) -> Any:
        weight = weight or 1.0

        if node_key is None or plane is None:
            return

        return PlaneGoal(node_key, plane_to_compas(plane), weight)
