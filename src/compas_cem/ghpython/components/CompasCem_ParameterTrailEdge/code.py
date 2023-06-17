"""
Set the length of a trail edge as an optimization parameter.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import TrailEdgeParameter


class TrailEdgeParameterComponent(component):
    def RunScript(self, edge_key, bound_low, bound_up):
        if not edge_key:
            return

        return TrailEdgeParameter(edge_key, bound_low, bound_up)