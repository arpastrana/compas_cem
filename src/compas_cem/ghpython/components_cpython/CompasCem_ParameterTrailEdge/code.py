# r: compas_cem>=0.9.0
"""
Set the length of a trail edge as an optimization parameter.
"""

from __future__ import annotations

from typing import Any

import Grasshopper

from compas_cem.optimization import TrailEdgeParameter


class TrailEdgeParameterComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        edge_key: Any,
        bound_low: float | None,
        bound_up: float | None,
    ) -> Any:
        if not edge_key:
            return

        return TrailEdgeParameter(edge_key, bound_low, bound_up)
