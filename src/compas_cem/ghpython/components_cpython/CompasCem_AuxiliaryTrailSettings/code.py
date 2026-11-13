# r: compas_cem>=0.10.0
"""
Set the length, state and direction of the auxiliary trails that Assemble Topology Diagram adds.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import Rhino

from compas_cem.ghpython import AuxiliaryTrailSettings


class AuxiliaryTrailSettingsComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        length: float | None,
        state: float | None,
        vector: Rhino.Geometry.Vector3d | None,
    ) -> Any:
        values = {"length": length, "state": state}
        if vector is not None:
            vector_xyz = (vector.X, vector.Y, vector.Z)
            values["vector"] = vector_xyz
        given = {name: value for name, value in values.items() if value is not None}

        try:
            settings = AuxiliaryTrailSettings(**given)
        except ValueError as error:
            warning = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(warning, str(error))  # noqa: F821
            return

        return settings
