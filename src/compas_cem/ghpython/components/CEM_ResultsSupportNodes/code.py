"""
Get reaction forces at the support nodes of a form diagram.
"""
from ghpythonlib.componentbase import executingcomponent as component

import rhinoscriptsyntax as rs


class ReactionForcesComponent(component):
    def RunScript(self, form, support_node_keys):
        if not form:
            return

        support_node_keys = support_node_keys or list(form.support_nodes())
        reaction_forces = [rs.AddPoint(*form.reaction_force(nd)) for nd in support_node_keys]

        return reaction_forces
