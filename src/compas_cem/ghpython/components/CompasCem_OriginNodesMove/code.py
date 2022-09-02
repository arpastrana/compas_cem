"""
Move the origin nodes of a topology diagram to a new location.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas.utilities import iterable_like
from compas_rhino.geometry import RhinoPoint


class MoveOriginNodesComponent(component):
    def RunScript(self, topology, origin_node_keys, points):
        if not topology or not origin_node_keys or not points:
            return

        topology = topology.copy()
        points = iterable_like(origin_node_keys, points, points[-1])

        for node_key, point in zip(origin_node_keys, points):
            point = RhinoPoint.from_geometry(point).to_compas()
            topology.node_attributes(node_key, names="xyz", values=point)

        return topology
