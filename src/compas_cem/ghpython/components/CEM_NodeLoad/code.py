"""
Create a load vector to be applied at a node.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_rhino.geometry import RhinoPoint
from compas_rhino.geometry import RhinoVector

from compas_cem.loads import NodeLoad


class NodeLoadComponent(component):
    def RunScript(self, point, vector):
        if not (point and vector):
            return

        point = RhinoPoint.from_geometry(point).to_compas()
        vector = RhinoVector.from_geometry(vector).to_compas()

        return NodeLoad.from_point_and_vector(point, vector)
