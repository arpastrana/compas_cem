# r: compas_cem>=0.9.0
"""
Disassemble a form diagram into its constituent parts.
"""

from __future__ import annotations

from typing import Any

import Grasshopper


class FormDisassemblyComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self, form: Any) -> Any:
        if not form:
            return

        edge_keys = list(form.edges())
        node_keys = list(form.nodes())
        support_node_keys = list(form.support_nodes())

        return node_keys, support_node_keys, edge_keys
