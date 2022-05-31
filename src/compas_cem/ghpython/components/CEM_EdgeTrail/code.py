"""
Create a trail edge from a rhino line.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas.geometry import Plane
from compas.geometry import cross_vectors

from compas_rhino.geometry import RhinoLine
from compas_rhino.geometry import RhinoPlane

from compas_cem.elements import TrailEdge


class TrailEdgeComponent(component):
    def RunScript(self, line, length, plane):
        if plane is not None:
            plane = RhinoPlane.from_geometry(plane).to_compas()
            plane = Plane(plane.point, cross_vectors(plane.xaxis, plane.yaxis))
        if line and length is not None:
            line = RhinoLine.from_geometry(line).to_compas()
            return TrailEdge.from_line(line, length=length, plane=plane)
