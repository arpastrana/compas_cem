"""
Search a node key in a topology or a form diagram using a point.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas.utilities import geometric_key
from compas_rhino.geometry import RhinoLine


class EdgeSearchComponent(component):
    def RunScript(self, diagram, line):
        if diagram and line:

            edge = []
            for ln in line:
                ln = RhinoLine.from_geometry(ln).to_compas()

                eg = []
                for point in (ln.start, ln.end):
                    gkey = geometric_key(point, diagram.tol)
                    node = diagram.gkey_node[gkey]
                    eg.append(node)
                edge.append(tuple(eg))

            return edge
