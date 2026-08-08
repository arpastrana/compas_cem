# r: compas_cem>=0.9.0
"""
Create a load vector to be applied at a node.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import Rhino

from compas_rhino.conversions import point_to_compas
from compas_rhino.conversions import vector_to_compas

from compas_cem.loads import NodeLoad


class NodeLoadComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        point: Rhino.Geometry.Point3d | None,
        vector: Rhino.Geometry.Vector3d | None,
    ) -> Any:
        if not (point and vector):
            return

        return NodeLoad.from_point_and_vector(
            point_to_compas(point), vector_to_compas(vector)
        )
