# r: compas_cem>=0.10.0
"""
Export a COMPAS CEM diagram and save it as a JSON file.
"""

from __future__ import annotations

import os
from typing import Any

import Grasshopper


class DiagramToJSON(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        export: bool | None,
        diagram: Any,
        filepath: str | None,
    ) -> Any:
        if not (export and diagram and filepath):
            return

        json_path = os.path.abspath(filepath)
        diagram.to_json(json_path, pretty=True)
        json_string = diagram.to_jsonstring(pretty=True)

        return json_string
