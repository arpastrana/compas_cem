"""
Disassemble a form diagram into its constituent parts.
"""
from ghpythonlib.componentbase import executingcomponent as component


class FormDisassemblyComponent(component):
    def RunScript(self, form):
        if not form:
            return

        edge_keys = list(form.edges())
        node_keys = list(form.nodes())
        support_node_keys = list(form.support_nodes())

        return node_keys, support_node_keys, edge_keys
