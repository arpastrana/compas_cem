"""
Create a deviation edge from a rhino line.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.elements import DeviationEdge

from compas_rhino.geometry import RhinoLine


class DeviationEdgeComponent(component):
    def RunScript(self, line, force):
        if line and force is not None:
            line = RhinoLine.from_geometry(line).to_compas()
            return DeviationEdge.from_line(line)
