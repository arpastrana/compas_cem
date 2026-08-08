"""
Pull the position of a node to a target polyline.
"""

from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import PolylineGoal
from compas_rhino.geometry import RhinoPolyline


class PolylineGoalComponent(component):
    def RunScript(self, node_key, polyline, weight):
        weight = weight or 1.0
        if node_key is None or not polyline:
            return
        polyline = RhinoPolyline.from_geometry(polyline).to_compas()
        return PolylineGoal(node_key, polyline, weight)
