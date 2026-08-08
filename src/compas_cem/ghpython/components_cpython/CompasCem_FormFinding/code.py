# r: compas_cem>=0.9.0
"""
Generate a form diagram in static equilibrium.
"""

from __future__ import annotations

from typing import Any

import Grasshopper

from compas_cem.equilibrium import static_equilibrium


class FormFindingComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        topology: Any,
        kmax: int | None,
        tmax: int | None,
        eta: float | None,
    ) -> Any:
        eta = eta or 1e-6
        tmax = tmax or 100

        if not topology:
            return

        return static_equilibrium(topology, kmax=kmax, tmax=tmax, eta=eta)
