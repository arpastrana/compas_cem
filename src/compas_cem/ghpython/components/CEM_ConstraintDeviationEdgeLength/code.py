"""
Make the length of a deviation edge to reach a goal length value.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import DeviationEdgeLengthConstraint


class DeviationEdgeLengthConstraintComponent(component):
    def RunScript(self, edge_key, length, weight):
        weight = weight or 1.0
        if edge_key and length is not None:
            return DeviationEdgeLengthConstraint(edge_key, length, weight)