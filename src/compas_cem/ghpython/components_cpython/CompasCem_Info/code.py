# r: compas_cem>=0.9.0
"""
Displays information about the active COMPAS CEM version and environment.
"""

from __future__ import annotations

import os
from typing import Any

import Grasshopper

import compas_cem


class Info(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self) -> Any:
        try:
            import compas_bootstrapper

            environment_name = compas_bootstrapper.ENVIRONMENT_NAME
        except ImportError:
            environment_name = os.path.dirname(compas_cem.__file__)
            environment_name = os.path.abspath(os.path.join(environment_name, ".."))

        ghenv.Component.Message = "COMPAS CEM v{}".format(compas_cem.__version__)  # noqa: F821

        info = "COMPAS CEM Version: {}\nEnvironment: {}"

        return info.format(compas_cem.__version__, environment_name)
