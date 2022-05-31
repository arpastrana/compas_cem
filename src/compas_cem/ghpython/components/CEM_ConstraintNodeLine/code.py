"""
Pull the position of a node to a target line ray.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import LineConstraint
from compas_rhino.geometry import RhinoLine


class LineConstraintComponent(component):
    def RunScript(self, node_key, line, weight):
        weight = weight or 1.0
        if node_key is None or not line:
            return
        line = RhinoLine.from_geometry(line).to_compas()
        return LineConstraint(node_key, line, weight)
