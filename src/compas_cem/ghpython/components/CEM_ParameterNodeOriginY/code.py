"""
Set the Y coordinate of an origin node as an optimization parameter.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import OriginNodeYParameter


class OriginNodeYParameterComponent(component):
    def RunScript(self, node_key, bound_low, bound_up):
        if node_key is not None and bound_low is not None and bound_up is not None:
            return OriginNodeYParameter(node_key, bound_low, bound_up)
