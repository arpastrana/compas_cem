"""
Generate a form diagram in static equilibrium.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem import PROXY_PORT

from compas.rpc import Proxy


class ConstrainedFormFindingComponent(component):
    def RunScript(self, topology, constraints, parameters, algorithm, iters_max, eps, tmax, eta):
        algorithm = algorithm or "LD_SLSQP"
        iters_max = iters_max or 100
        eps = eps or 1e-6
        tmax = tmax or 100
        eta = eta or 1e-6

        if topology and constraints and parameters:
            topology = topology.copy()

            with Proxy("compas_cem.optimization", port=PROXY_PORT) as opt:
                solution = opt.solve_nlopt_proxy(topology,
                                                 constraints,
                                                 parameters,
                                                 algorithm,
                                                 iters_max,
                                                 eps,
                                                 tmax,
                                                 eta)

            form, objective, grad_norm, iters, time, status = solution
            return form, objective, grad_norm, iters, time, status
