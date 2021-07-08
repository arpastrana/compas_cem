"""
Automatically find the trails in a topology diagram. The diagram is modified in-place.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_rhino.geometry import RhinoVector


class BuildTopologyDiagramComponent(component):
    def RunScript(self, topology, add_auxiliary_trails, auxiliary_trail_length, auxiliary_trail_vector):
        add_auxiliary_trails = add_auxiliary_trails or False

        if topology:

            topology = topology.copy()

            if auxiliary_trail_length:
                topology.auxiliary_trail_length = auxiliary_trail_length
            if auxiliary_trail_vector:
                topology.auxiliary_trail_vector = RhinoVector.from_geometry(auxiliary_trail_vector).to_compas()

            topology.build_trails(add_auxiliary_trails)

            trails = list(topology.trails())
            auxiliary_trails = list(topology.auxiliary_trail_edges())

            return topology, trails, auxiliary_trails
