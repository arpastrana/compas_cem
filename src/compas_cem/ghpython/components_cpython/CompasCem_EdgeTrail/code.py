# r: compas_cem>=0.9.1
"""
Create a trail edge from a rhino line.
"""

from __future__ import annotations

from math import copysign
from typing import Any

import Grasshopper
import Rhino

from compas_rhino.conversions import line_to_compas
from compas_rhino.conversions import plane_to_compas

from compas_cem.elements import TrailEdge


class TrailEdgeComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        line: Rhino.Geometry.Line | None,
        state: float | None,
        length: float | None,
        plane: Rhino.Geometry.Plane | None,
    ) -> Any:
        if not line:
            return

        warning = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning

        if length is not None and plane is not None:
            message = "Connect either a length or a plane, not both."
            ghenv.Component.AddRuntimeMessage(warning, message)
            return

        edge_line = line_to_compas(line)

        if plane is not None:
            # The plane's position sets the state; the unit length applies only if the trail never meets it.
            target_plane = plane_to_compas(plane)
            trail_edge = TrailEdge.from_line(edge_line, length=1.0, plane=target_plane)
            return trail_edge

        if length is None or state is None:
            return

        if state == 0.0:
            message = "The state must be nonzero: positive for tension, negative for compression."
            ghenv.Component.AddRuntimeMessage(warning, message)
            return

        signed_length = copysign(abs(length), state)
        trail_edge = TrailEdge.from_line(edge_line, length=signed_length)

        return trail_edge
