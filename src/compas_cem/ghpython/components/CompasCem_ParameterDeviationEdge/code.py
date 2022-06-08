"""
Set the force of a deviation edge as an optimization parameter.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import DeviationEdgeParameter


class DeviationEdgeParameterComponent(component):
    def RunScript(self, edge_key, bound_low, bound_up):
        if not edge_key or bound_low is None or bound_up is None:
            return

        return DeviationEdgeParameter(edge_key, bound_low, bound_up)
