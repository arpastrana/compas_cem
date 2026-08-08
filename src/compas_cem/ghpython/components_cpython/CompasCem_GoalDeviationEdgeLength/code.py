"""
Make the length of a deviation edge reach a target value.
"""

from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.optimization import DeviationEdgeLengthGoal


class DeviationEdgeLengthGoalComponent(component):
    def RunScript(self, edge_key, length, weight):
        weight = weight or 1.0
        if not edge_key or length is None:
            return
        return DeviationEdgeLengthGoal(edge_key, length, weight)
