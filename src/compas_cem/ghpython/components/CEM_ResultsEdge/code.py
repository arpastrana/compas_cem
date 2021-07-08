"""
Extract the post form-finding results of the edges in a form diagram.
"""
from ghpythonlib.componentbase import executingcomponent as component


class EdgeResultsComponent(component):
    def RunScript(self, form, edge):
        if form:
            edge = edge or list(form.edges())
            length = [form.edge_length_2(ed) for ed in edge]
            force = [form.edge_force(ed) for ed in edge]
            return length, force
