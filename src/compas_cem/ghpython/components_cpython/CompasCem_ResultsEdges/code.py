# r: compas_cem>=0.9.0
"""
Get the lengths and forces of the edges in a form diagram.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import System


class EdgeResultsComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        form: Any,
        edge_keys: System.Collections.Generic.List[object],
    ) -> Any:
        if not form:
            return

        edge_keys = edge_keys or list(form.edges())
        lengths = [form.edge_length_2(edge) for edge in edge_keys]
        forces = [form.edge_force(edge) for edge in edge_keys]

        return lengths, forces
