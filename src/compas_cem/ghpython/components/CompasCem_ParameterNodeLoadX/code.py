"""
Set the X component of a node load as an optimization parameter.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import NodeLoadXParameter


class NodeLoadXParameterComponent(component):
    def RunScript(self, node_key, bound_low, bound_up):
        if node_key is None:
            return

        return NodeLoadXParameter(node_key, bound_low, bound_up)
