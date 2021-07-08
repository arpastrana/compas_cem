"""
Create a trail edge from a rhino line.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.elements import TrailEdge


class TrailEdgeComponent(component):
    def RunScript(self, line, length):
        if line and length is not None:
            return TrailEdge.from_rhino_line(line, length)
