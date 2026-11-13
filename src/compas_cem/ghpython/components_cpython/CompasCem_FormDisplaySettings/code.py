# r: compas_cem>=0.10.0
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
        arrow_min: float | None,
        arrow_scale: float | None,
        width_min: float | None,
        width_max: float | None,
        radius_min: float | None,
        radius_max: float | None,
        thick_sides: int | None,
    ) -> Any:
        values = {
            "arrow_min": arrow_min,
            "arrow_scale": arrow_scale,
            "width_min": width_min,
            "width_max": width_max,
            "radius_min": radius_min,
            "radius_max": radius_max,
            "thick_sides": thick_sides,
        }
        given = {name: value for name, value in values.items() if value is not None}
        settings = FormDisplaySettings(**given)

        return settings
