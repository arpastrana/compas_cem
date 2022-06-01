"""
Make the force on a trail edge to reach a prescribed value.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import TrailEdgeForceConstraint


class TrailEdgeForceConstraintComponent(component):
    def RunScript(self, edge_key, force, weight):
        weight = weight or 1.0
        if not edge_key or force is None:
            return
        return TrailEdgeForceConstraint(edge_key, force, weight)
