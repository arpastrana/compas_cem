"""
Displays information about the active COMPAS CEM version and environment.
"""
import compas_bootstrapper
from ghpythonlib.componentbase import executingcomponent as component

import compas_cem


class Info(component):
    def RunScript(self):
        self.Message = 'COMPAS CEM v{}'.format(compas_cem.__version__)
        info = 'COMPAS CEM Version: {}\nEnvironment: {}'
        return (info.format(compas_cem.__version__, compas_bootstrapper.ENVIRONMENT_NAME))
