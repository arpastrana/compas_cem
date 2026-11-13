# r: compas_cem>=0.9.1
"""
Create a trail edge from a line.
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

        if state == 0.0:
            message = "The state must be nonzero: positive for tension, negative for compression."
            ghenv.Component.AddRuntimeMessage(warning, message)
            return

        edge_line = line_to_compas(line)

        if plane is not None:
            # The state signs the unit length, which the trail takes only if it never meets the plane.
            target_plane = plane_to_compas(plane)
            unit_length = 1.0 if state is None else copysign(1.0, state)
            trail_edge = TrailEdge.from_line(
                edge_line, length=unit_length, plane=target_plane
            )
            return trail_edge

        if length is None:
            message = "Connect a length or a plane."
            ghenv.Component.AddRuntimeMessage(warning, message)
            return

        if state is None:
            message = "Connect a state to sign the length: positive for tension, negative for compression."
            ghenv.Component.AddRuntimeMessage(warning, message)
            return

        signed_length = copysign(abs(length), state)
        trail_edge = TrailEdge.from_line(edge_line, length=signed_length)

        return trail_edge
