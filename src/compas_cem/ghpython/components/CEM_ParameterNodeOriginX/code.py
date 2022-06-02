"""
Set the X coordinate of an origin node as an optimization parameter.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import OriginNodeXParameter


class OriginNodeXParameterComponent(component):
    def RunScript(self, node_key, bound_low, bound_up):
        if node_key is None or bound_low is None or bound_up is None:
            return

        return OriginNodeXParameter(node_key, bound_low, bound_up)
