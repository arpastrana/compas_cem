"""
Pull the position of a node to a target plane.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas.geometry import Plane
from compas.geometry import cross_vectors

from compas_rhino.geometry import RhinoPlane
from compas_cem.optimization import PlaneConstraint


class PlaneConstraintComponent(component):
    def RunScript(self, node_key, plane, weight):
        weight = weight or 1.0
        if node_key is not None and plane is not None:
            plane = RhinoPlane.from_geometry(plane).to_compas()
            plane = Plane(plane.point, cross_vectors(plane.xaxis, plane.yaxis))
            return PlaneConstraint(node_key, plane, weight)
