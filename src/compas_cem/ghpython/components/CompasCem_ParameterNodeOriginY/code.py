"""
Set the Y coordinate of an origin node as an optimization parameter.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import OriginNodeYParameter


class OriginNodeYParameterComponent(component):
    def RunScript(self, node_key, bound_low, bound_up):
        if node_key is None or bound_low is None or bound_up is None:
            return

        return OriginNodeYParameter(node_key, bound_low, bound_up)
