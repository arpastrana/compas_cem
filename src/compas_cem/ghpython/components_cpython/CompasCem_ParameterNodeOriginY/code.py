# r: compas_cem>=0.9.0
"""
Set the Y coordinate of an origin node as an optimization parameter.
"""

from __future__ import annotations

from typing import Any

import Grasshopper

from compas_cem.optimization import OriginNodeYParameter


class OriginNodeYParameterComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        node_key: int | None,
        bound_low: float | None,
        bound_up: float | None,
    ) -> Any:
        if node_key is None:
            return

        return OriginNodeYParameter(node_key, bound_low, bound_up)
