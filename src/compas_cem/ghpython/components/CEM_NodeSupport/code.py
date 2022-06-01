"""
Create a node support from a point.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_rhino.geometry import RhinoPoint
from compas_cem.supports import NodeSupport


class NodeSupportComponent(component):
    def RunScript(self, point):
        if not point:
            return

        xyz = RhinoPoint.from_geometry(point).to_compas()
        return NodeSupport.from_point(xyz)
