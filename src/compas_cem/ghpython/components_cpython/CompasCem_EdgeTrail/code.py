# r: compas_cem>=0.9.0
"""
Create a trail edge from a rhino line.
"""

from __future__ import annotations

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
        length: float | None,
        plane: Rhino.Geometry.Plane | None,
    ) -> Any:
        if not line or length is None:
            return

        target_plane = None
        if plane is not None:
            target_plane = plane_to_compas(plane)

        return TrailEdge.from_line(
            line_to_compas(line), length=length, plane=target_plane
        )
