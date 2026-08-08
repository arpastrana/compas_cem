# r: compas_cem>=0.9.0
"""
Create a node support from a point.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import Rhino

from compas_rhino.conversions import point_to_compas

from compas_cem.supports import NodeSupport


class NodeSupportComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self, point: Rhino.Geometry.Point3d | None) -> Any:
        if not point:
            return

        return NodeSupport.from_point(point_to_compas(point))
