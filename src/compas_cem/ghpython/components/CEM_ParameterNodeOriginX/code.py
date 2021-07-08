"""
Set the X coordinate of an origin node as an optimization parameter.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import OriginNodeXParameter


class OriginNodeXParameterComponent(component):
    def RunScript(self, node_key, bound_low, bound_up):
        if node_key is not None and bound_low is not None and bound_up is not None:
            return OriginNodeXParameter(node_key, bound_low, bound_up)
