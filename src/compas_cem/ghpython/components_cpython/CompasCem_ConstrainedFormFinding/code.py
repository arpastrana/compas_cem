# r: compas_cem>=0.10.0
"""
Find a form diagram in static equilibrium that best meets the goals, by optimizing the parameters.
"""

from __future__ import annotations

from typing import Any

import Grasshopper
import System

from compas_cem.optimization import Optimizer


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

        optimizer = Optimizer()
        for goal in goals:
            optimizer.add_goal(goal)
        for parameter in parameters:
            optimizer.add_parameter(parameter)

        form = optimizer.solve(
            topology=topology,
            algorithm=algorithm,
            iters=iters_max,
            eps=eps,
            kappa=kappa,
            tmax=tmax,
            eta=eta,
        )

        objective = optimizer.penalty
        grad_norm = optimizer.gradient_norm
        iters = optimizer.evals
        time = optimizer.time_opt
        status = optimizer.status

        return topology, form, objective, grad_norm, iters, time, status
