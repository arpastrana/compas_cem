"""
Search for an edge key in a topology or a form diagram using a line.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_rhino.geometry import RhinoLine
from compas.utilities import geometric_key


class SearchEdgeKeyComponent(component):
    def RunScript(self, diagram, line):
        if not (diagram and line):
            return

        line = RhinoLine.from_geometry(line).to_compas()

        eg = []
        for point in (line.start, line.end):
            gkey = geometric_key(point, diagram.tol)
            node = diagram.gkey_node[gkey]
            eg.append(node)

        return [tuple(eg)]
