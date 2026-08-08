# r: compas_cem>=0.9.0
"""
Move the origin nodes of a topology diagram to a new location.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import Rhino
import System

from compas.itertools import iterable_like
from compas_rhino.conversions import point_to_compas


class MoveOriginNodesComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        topology: Any,
        origin_node_keys: System.Collections.Generic.List[int],
        points: System.Collections.Generic.List[Rhino.Geometry.Point3d],
    ) -> Any:
        if not topology or not origin_node_keys or not points:
            return

        topology = topology.copy()
        targets = iterable_like(origin_node_keys, points, points[-1])

        for node_key, point in zip(origin_node_keys, targets):
            xyz = point_to_compas(point)
            topology.node_attributes(node_key, names="xyz", values=xyz)

        return topology
