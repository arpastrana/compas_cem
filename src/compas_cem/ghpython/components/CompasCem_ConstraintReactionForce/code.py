"""
Make the reaction force on a trail edge to meet a target force vector.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_rhino.geometry import RhinoVector
from compas_cem.optimization import ReactionForceConstraint


class ReactionForceConstraintComponent(component):
    def RunScript(self, node_key, vector, weight):
        weight = weight or 1.0
        if node_key is None or not vector:
            return
        vector = RhinoVector.from_geometry(vector).to_compas()
        return ReactionForceConstraint(node_key, vector, weight)
