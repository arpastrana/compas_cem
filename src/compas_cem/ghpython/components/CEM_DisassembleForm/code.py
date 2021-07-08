"""
Disassemble a form diagram into its constituent parts.
"""
from ghpythonlib.componentbase import executingcomponent as component


class FormDisassemblyComponent(component):
    def RunScript(self, form):
        if form:
            edges = list(form.edges())
            nodes = list(form.nodes())
            support_nodes = list(form.support_nodes())

            return nodes, support_nodes, edges
