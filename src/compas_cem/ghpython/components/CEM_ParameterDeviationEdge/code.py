"""
Set the force of a deviation edge as an optimization parameter.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import DeviationEdgeParameter


class DeviationEdgeParameterComponent(component):
    def RunScript(self, edge_key, bound_low, bound_up):
        if edge_key and bound_low is not None and bound_up is not None:
            return DeviationEdgeParameter(edge_key, bound_low, bound_up)
