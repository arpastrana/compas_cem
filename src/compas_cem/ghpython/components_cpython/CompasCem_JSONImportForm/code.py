# r: compas_cem>=0.10.0
"""
Import a COMPAS CEM form diagram from a JSON file.
"""

from __future__ import annotations

import os
from typing import Any

import Grasshopper

from compas_cem.diagrams import FormDiagram


class FormDiagramFromJSON(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self, read: bool | None, filepath: str | None) -> Any:
        if not (read and filepath):
            return

        json_path = os.path.abspath(filepath)
        form = FormDiagram.from_json(json_path)

        return form
