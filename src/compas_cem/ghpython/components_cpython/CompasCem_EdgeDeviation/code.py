# r: compas_cem>=0.10.0
"""
Create a deviation edge from a line.
"""

from __future__ import annotations

from math import copysign
from typing import Any

import Grasshopper
import Rhino

from compas_rhino.conversions import line_to_compas

from compas_cem.elements import DeviationEdge


class DeviationEdgeComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        line: Rhino.Geometry.Line | None,
        state: float | None,
        force: float | None,
    ) -> Any:
        if not line:
            return

        warning = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning

        if state is None:
            message = "Connect a state: positive for tension, negative for compression."
            ghenv.Component.AddRuntimeMessage(warning, message)
            return

        if force is None:
            message = "Connect a force."
            ghenv.Component.AddRuntimeMessage(warning, message)
            return

        if state == 0.0:
            message = "The state must be nonzero: positive for tension, negative for compression."
            ghenv.Component.AddRuntimeMessage(warning, message)
            return

        edge_line = line_to_compas(line)
        signed_force = copysign(abs(force), state)
        deviation_edge = DeviationEdge.from_line(edge_line, force=signed_force)

        return deviation_edge
