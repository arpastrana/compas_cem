"""
Create a trail edge from a rhino line.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_rhino.geometry import RhinoLine
from compas_rhino.geometry import RhinoPlane

from compas_cem.elements import TrailEdge


class TrailEdgeComponent(component):
    def RunScript(self, line, length, plane):
        if not line or length is None:
            return

        if plane is not None:
            plane = RhinoPlane.from_geometry(plane).to_compas()
        line = RhinoLine.from_geometry(line).to_compas()
        return TrailEdge.from_line(line, length=length, plane=plane)
