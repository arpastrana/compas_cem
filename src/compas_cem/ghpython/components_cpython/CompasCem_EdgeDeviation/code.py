# r: compas_cem>=0.9.0
"""
Create a deviation edge from a line.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import Rhino

from compas_rhino.conversions import line_to_compas

from compas_cem.elements import DeviationEdge


class DeviationEdgeComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self, line: Rhino.Geometry.Line | None, force: float | None) -> Any:
        if not line or force is None:
            return

        return DeviationEdge.from_line(line_to_compas(line), force=force)
