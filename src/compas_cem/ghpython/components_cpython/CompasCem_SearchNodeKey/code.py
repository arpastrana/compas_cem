# r: compas_cem>=0.9.0
"""
Search a node key in a topology or a form diagram using a point.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import Rhino

from compas.tolerance import TOL
from compas_rhino.conversions import point_to_compas


class SearchNodeKeyComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self, diagram: Any, point: Rhino.Geometry.Point3d | None) -> Any:
        if not (point and diagram):
            return

        pt = point_to_compas(point)
        gkey = TOL.geometric_key(pt, diagram.tol)

        return diagram.gkey_node[gkey]
