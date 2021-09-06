"""
Import a COMPAS CEM topology diagram from a JSON file.
"""
import os

from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.diagrams import TopologyDiagram


class FormDiagramFromJSON(component):
    def RunScript(self, filepath):
        if filepath:
            filepath = os.path.abspath(filepath)
            topology = TopologyDiagram.from_json(filepath)
            return topology
