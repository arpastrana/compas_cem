"""
Pull the position of a node to a target point.
"""

from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import PointGoal
from compas_rhino.geometry import RhinoPoint


class PointGoalComponent(component):
    def RunScript(self, node_key, point, weight):
        weight = weight or 1.0
        if node_key is None or not point:
            return
        point = RhinoPoint.from_geometry(point).to_compas()
        return PointGoal(node_key, point, weight)
