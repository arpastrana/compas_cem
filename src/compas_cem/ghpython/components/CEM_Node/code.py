"""
Create a node from a rhino point.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.elements import Node


class NodeComponent(component):
    def RunScript(self, point):
        if point:
            return Node.from_rhino_point(point)
