# r: compas_cem>=0.9.0
"""
Import a COMPAS CEM form diagram from a JSON file.
"""

from __future__ import annotations

import os
from typing import Any

import Grasshopper

from compas_cem.diagrams import FormDiagram


class FormDiagramFromJSON(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self, filepath: str | None) -> Any:
        if not filepath:
            return

        return FormDiagram.from_json(os.path.abspath(filepath))
