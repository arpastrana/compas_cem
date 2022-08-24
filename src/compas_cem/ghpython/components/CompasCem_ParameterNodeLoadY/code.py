"""
Set the Y component of a node load as an optimization parameter.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import NodeLoadYParameter


class NodeLoadYParameterComponent(component):
    def RunScript(self, node_key, bound_low, bound_up):
        if node_key is None:
            return

        return NodeLoadYParameter(node_key, bound_low, bound_up)
