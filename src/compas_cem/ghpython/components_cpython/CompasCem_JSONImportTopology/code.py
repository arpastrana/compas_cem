# r: compas_cem>=0.9.1
"""
Import a COMPAS CEM topology diagram from a JSON file.
"""

from __future__ import annotations

import os
from typing import Any

import Grasshopper

from compas_cem.diagrams import TopologyDiagram


class TopologyDiagramFromJSON(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self, read: bool | None, filepath: str | None) -> Any:
        if not (read and filepath):
            return

        json_path = os.path.abspath(filepath)
        topology = TopologyDiagram.from_json(json_path)

        return topology
