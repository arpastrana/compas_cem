# r: compas_cem>=0.9.0
"""
Get the artists color scheme for the objects of the CEM framework.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import System

from compas_cem import COLORS


class ArtistColorsComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self) -> Any:
        colors = {
            name: System.Drawing.Color.FromArgb(*rgb) for name, rgb in COLORS.items()
        }

        return (
            colors["tension"],
            colors["compression"],
            colors["edge"],
            colors["node"],
            colors["node_support"],
            colors["node_origin"],
            colors["load"],
            colors["support_force"],
            colors["trail"],
            colors["auxiliary_trail"],
        )
