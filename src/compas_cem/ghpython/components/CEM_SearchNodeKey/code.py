"""
Search a node key in a topology or a form diagram using a point.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas.utilities import geometric_key
from compas_rhino.geometry import RhinoPoint


class SearchNodeKeyComponent(component):
    def RunScript(self, diagram, point):
        if not (point and diagram):
            return

        pt = RhinoPoint.from_geometry(point).to_compas()
        gkey = geometric_key(pt, diagram.tol)

        return diagram.gkey_node[gkey]
