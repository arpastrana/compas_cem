# r: compas_cem>=0.9.0
"""
Generate a form diagram in static equilibrium such that it meets user-defined goals.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import System
from scriptcontext import sticky

from compas.rpc import Proxy


class ConstrainedFormFindingComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(
        self,
        solve: bool | None,
        topology: Any,
        goals: System.Collections.Generic.List[object],
        parameters: System.Collections.Generic.List[object],
        algorithm: str | None,
        iters_max: int | None,
        eps: float | None,
        kappa: float | None,
        tmax: int | None,
        eta: float | None,
    ) -> Any:
        algorithm = algorithm or "SLSQP"
        iters_max = iters_max or 100
        eps = eps or 1e-6
        kappa = kappa or 1e-8
        tmax = tmax or 100
        eta = eta or 1e-6

        if not (solve and topology and goals and parameters):
            return

        topology = topology.copy()

        # clean goals and parameters from None
        goals = [goal for goal in goals if goal is not None]
        parameters = [parameter for parameter in parameters if parameter is not None]

        # fetch optimization proxy from scriptcontext
        opt = sticky.get("proxy_cem")
        proxy_temp_exists = opt is not None

        # create temporary proxy server if unavailable from scriptcontext
        if not proxy_temp_exists:
            opt = Proxy("compas_cem.optimization")

        # solve constrained form-finding problem
        solution = opt.solve_proxy(
            topology=topology,
            goals=goals,
            parameters=parameters,
            algorithm=algorithm,
            iters=iters_max,
            eps=eps,
            kappa=kappa,
            tmax=tmax,
            eta=eta,
        )

        # shut down temporary proxy
        if not proxy_temp_exists:
            opt.stop_server()

        # unpack solution
        topology, form, objective, grad_norm, iters, time, status = solution

        return topology, form, objective, grad_norm, iters, time, status
