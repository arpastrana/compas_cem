"""
Generate a form diagram in static equilibrium.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.equilibrium import static_equilibrium


class FormFindingComponent(component):
    def RunScript(self, topology, tmax, eta):
        tmax = tmax or 100
        eta = eta or 1e-6
        if topology:
            return static_equilibrium(topology, tmax=tmax, eta=eta)
