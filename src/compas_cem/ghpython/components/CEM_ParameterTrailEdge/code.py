"""
Set the length of a trail edge as an optimization parameter.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import TrailEdgeParameter


class TrailEdgeParameterComponent(component):
    def RunScript(self, edge_key, bound_low, bound_up):
        if edge_key and bound_low is not None and bound_up is not None:
            return TrailEdgeParameter(edge_key, bound_low, bound_up)
