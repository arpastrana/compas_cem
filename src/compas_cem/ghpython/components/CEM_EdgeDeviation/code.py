"""
Create a deviation edge from a rhino line.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.elements import DeviationEdge


class DeviationEdgeComponent(component):
    def RunScript(self, line, force):
        if line and force is not None:
            return DeviationEdge.from_rhino_line(line, force=force)
