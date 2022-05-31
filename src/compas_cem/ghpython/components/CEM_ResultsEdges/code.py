"""
Get the lengths and forces of the edges in a form diagram.
"""
from ghpythonlib.componentbase import executingcomponent as component


class EdgeResultsComponent(component):
    def RunScript(self, form, edge_keys):
        if not form:
            return

        edge_keys = edge_keys or list(form.edges())
        lengths = [form.edge_length_2(ed) for ed in edge_keys]
        forces = [form.edge_force(ed) for ed in edge_keys]

        return lengths, forces
