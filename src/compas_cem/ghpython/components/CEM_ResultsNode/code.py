"""
Extract the post form-finding results of the nodes in a form diagram.
"""
from ghpythonlib.componentbase import executingcomponent as component

import rhinoscriptsyntax as rs


class NodeResultsComponent(component):
    def RunScript(self, form, node):
        if form:
            node = node or list(form.nodes())
            point = [rs.AddPoint(*form.node_xyz(nd)) for nd in node]
            reaction_force = [rs.AddPoint(*form.reaction_force(nd)) for nd in node]
            return point, reaction_force
