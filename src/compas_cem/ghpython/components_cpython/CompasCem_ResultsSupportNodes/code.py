# r: compas_cem>=0.9.0
"""
Get reaction forces at the support nodes of a form diagram.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import System

from compas_rhino.conversions import point_to_rhino


class ReactionForcesComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        form: Any,
        support_node_keys: System.Collections.Generic.List[int],
    ) -> Any:
        if not form:
            return

        support_node_keys = support_node_keys or list(form.support_nodes())

        return [point_to_rhino(form.reaction_force(node)) for node in support_node_keys]
