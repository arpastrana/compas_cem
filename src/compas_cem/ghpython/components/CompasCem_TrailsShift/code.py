"""
Shift the starting sequence of a selection of trails in a topology diagram.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas.utilities import iterable_like
from compas_rhino.geometry import RhinoPoint


class ShiftTrailsSequenceComponent(component):
    def RunScript(self, topology, origin_node_keys, sequences):
        if not topology or not origin_node_keys or not sequences:
            return

        topology = topology.copy()
        sequences = iterable_like(origin_node_keys, sequences, sequences[-1])

        for node_key, sequence in zip(origin_node_keys, sequences):
            topology.shift_trail(node_key, sequence)

        return topology
