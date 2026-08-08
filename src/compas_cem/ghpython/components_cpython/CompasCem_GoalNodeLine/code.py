"""
Pull the position of a node to a target line ray.
"""

from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import LineGoal
from compas_rhino.geometry import RhinoLine


class LineGoalComponent(component):
    def RunScript(self, node_key, line, weight):
        weight = weight or 1.0
        if node_key is None or not line:
            return
        line = RhinoLine.from_geometry(line).to_compas()
        return LineGoal(node_key, line, weight)
