"""
Create a node support from a rhino point.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.supports import NodeSupport


class NodeSupportComponent(component):
    def RunScript(self, point):
        if point:
            return NodeSupport.from_rhino_point(point)
