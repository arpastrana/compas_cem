# r: compas_cem>=0.10.0
"""
Set the X coordinate of an origin node as an optimization parameter.
"""

from __future__ import annotations

from typing import Any

import Grasshopper

from compas_cem.optimization import OriginNodeXParameter


class OriginNodeXParameterComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        node_key: int | None,
        bound_low: float | None,
        bound_up: float | None,
    ) -> Any:
        if node_key is None:
            return

        parameter = OriginNodeXParameter(
            node_key, bound_low, bound_up, is_absolute=True
        )

        return parameter
