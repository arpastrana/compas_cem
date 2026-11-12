# r: compas_cem>=0.9.1
"""
Set how Draw Form draws a form diagram.
"""

from __future__ import annotations

from typing import Any

import Grasshopper

from compas_cem.ghpython import FormDisplaySettings


class FormDisplaySettingsComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        force_min: float | None,
        force_scale: float | None,
        width_min: float | None,
        width_max: float | None,
        radius_min: float | None,
        radius_max: float | None,
        show_labels: bool | None,
    ) -> Any:
        values = {
            "force_min": force_min,
            "force_scale": force_scale,
            "width_min": width_min,
            "width_max": width_max,
            "radius_min": radius_min,
            "radius_max": radius_max,
            "show_labels": show_labels,
        }
        given = {name: value for name, value in values.items() if value is not None}
        settings = FormDisplaySettings(**given)

        return settings
