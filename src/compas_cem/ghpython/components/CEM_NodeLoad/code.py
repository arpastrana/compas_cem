"""
Create a load vector to be applied at a node.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.loads import NodeLoad


class NodeLoadComponent(component):
    def RunScript(self, point, vector):
        if point and vector:
            return NodeLoad.from_rhino_point_and_vector(point, vector)
