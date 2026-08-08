# r: compas_cem>=0.9.0
"""
Search for an edge key in a topology or a form diagram using a line.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import Rhino

from compas.tolerance import TOL
from compas_rhino.conversions import line_to_compas


class SearchEdgeKeyComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self, diagram: Any, line: Rhino.Geometry.Line | None) -> Any:
        if not (diagram and line):
            return

        segment = line_to_compas(line)

        eg = []
        for point in (segment.start, segment.end):
            gkey = TOL.geometric_key(point, diagram.tol)
            node = diagram.gkey_node[gkey]
            eg.append(node)

        return [tuple(eg)]
