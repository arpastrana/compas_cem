"""
Import a COMPAS CEM form diagram from a JSON file.
"""
import os

from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.diagrams import FormDiagram


class FormDiagramFromJSON(component):
    def RunScript(self, filepath):
        if not filepath:
            return

        filepath = os.path.abspath(filepath)
        form = FormDiagram.from_json(filepath)
        return form
