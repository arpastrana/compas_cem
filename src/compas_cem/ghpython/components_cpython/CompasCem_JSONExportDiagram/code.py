# r: compas_cem>=0.9.0
"""
Export a COMPAS CEM diagram and save it as a JSON file.
"""

from __future__ import annotations

import os
from typing import Any

import Grasshopper


class DiagramToJSON(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self, diagram: Any, filepath: str | None) -> Any:
        if not (diagram and filepath):
            return

        diagram.to_json(os.path.abspath(filepath), pretty=True)

        return diagram.data
