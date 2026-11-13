# r: compas_cem>=0.9.1
"""
Get the signed forces of the edges in a form diagram.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import System


class EdgeForcesComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        form: Any,
        edge_keys: System.Collections.Generic.List[object],
    ) -> Any:
        if not form:
            return

        edge_keys = edge_keys or list(form.edges())
        forces = [form.edge_force(edge) for edge in edge_keys]

        return forces
