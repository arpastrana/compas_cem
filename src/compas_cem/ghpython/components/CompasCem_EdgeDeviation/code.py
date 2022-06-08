"""
Create a deviation edge from a line.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.elements import DeviationEdge

from compas_rhino.geometry import RhinoLine


class DeviationEdgeComponent(component):
    def RunScript(self, line, force):
        if not line or force is None:
            return
        line = RhinoLine.from_geometry(line).to_compas()
        return DeviationEdge.from_line(line, force=force)
