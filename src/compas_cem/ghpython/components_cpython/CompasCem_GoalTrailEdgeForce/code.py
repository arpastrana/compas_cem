# r: compas_cem>=0.9.0
"""
Make the force on a trail edge to reach a prescribed value.
"""

from __future__ import annotations

from typing import Any

import Grasshopper

from compas_cem.optimization import TrailEdgeForceGoal


class TrailEdgeForceGoalComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        edge_key: Any,
        force: float | None,
        weight: float | None,
    ) -> Any:
        weight = weight or 1.0

        if not edge_key or force is None:
            return

        return TrailEdgeForceGoal(edge_key, force, weight)
