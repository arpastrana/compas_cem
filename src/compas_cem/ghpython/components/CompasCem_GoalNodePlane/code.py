"""
Pull the position of a node to a target plane.
"""

from ghpythonlib.componentbase import executingcomponent as component

from compas_rhino.geometry import RhinoPlane
from compas_cem.optimization import PlaneGoal


class PlaneGoalComponent(component):
    def RunScript(self, node_key, plane, weight):
        weight = weight or 1.0
        if node_key is None or plane is None:
            return
        plane = RhinoPlane.from_geometry(plane).to_compas()
        return PlaneGoal(node_key, plane, weight)
