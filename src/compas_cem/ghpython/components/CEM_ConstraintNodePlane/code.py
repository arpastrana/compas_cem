"""
Pull the position of a node to a target plane.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import PlaneConstraint
from compas_rhino.geometry import RhinoPlane


class PlaneConstraintComponent(component):
    def RunScript(self, node_key, plane, weight):
        weight = weight or 1.0
        if node_key is not None and plane:
            plane = RhinoPlane.from_geometry(plane).to_compas()
            return PlaneConstraint(node_key, plane, weight)
