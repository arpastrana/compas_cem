"""
Align the direction of a trail or a deviation edge with a target vector.
"""

from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import EdgeDirectionConstraint
from compas_rhino.geometry import RhinoVector


class EdgeDirectionConstraintComponent(component):
    def RunScript(self, edge_key, vector, weight):
        weight = weight or 1.0
        if not edge_key or not vector:
            return
        vector = RhinoVector.from_geometry(vector).to_compas()
        return EdgeDirectionConstraint(edge_key, vector, weight)
