# r: compas_cem>=0.9.0
"""
Set the force of a deviation edge as an optimization parameter.
"""

from __future__ import annotations

from typing import Any

import Grasshopper

from compas_cem.optimization import DeviationEdgeParameter


class DeviationEdgeParameterComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        edge_key: Any,
        bound_low: float | None,
        bound_up: float | None,
    ) -> Any:
        if not edge_key:
            return

        return DeviationEdgeParameter(edge_key, bound_low, bound_up)
