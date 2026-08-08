# r: compas_cem>=0.9.0
"""
Draw a form diagram.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import System

from compas_cem.ghpython import FormDiagramObject


class FormArtistComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        form: Any,
        node_keys: System.Collections.Generic.List[int],
        edge_keys: System.Collections.Generic.List[object],
        force_min: float | None,
        force_scale: float | None,
    ) -> Any:
        node_keys = node_keys or None
        edge_keys = edge_keys or None
        force_min = force_min or 1e-3
        force_scale = force_scale or 1.0

        if not form:
            return

        obj = FormDiagramObject(form)

        nodes = obj.draw_nodes(node_keys)
        edges = obj.draw_edges(edge_keys)
        support_nodes = obj.draw_nodes_support(node_keys)

        loads = obj.draw_loads(node_keys, min_load=force_min, scale=force_scale)
        reactions = obj.draw_reactions(
            node_keys, min_force=force_min, scale=force_scale
        )

        return nodes, support_nodes, edges, loads, reactions
