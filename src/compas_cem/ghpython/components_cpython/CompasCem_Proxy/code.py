# r: compas_cem>=0.9.0
"""
Create an RPC proxy server to solve a constrained form-finding problem via CPython
"""

from __future__ import annotations

from typing import Any

import Grasshopper
from scriptcontext import sticky

from compas.rpc import Proxy

from compas_cem import PROXY_PORT


class CEMProxyComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self, start: bool | None, stop: bool | None) -> Any:
        if not (start or stop):
            return

        if start:
            proxy = Proxy("compas_cem.optimization", port=PROXY_PORT)
            sticky["proxy_cem"] = proxy

        if stop:
            proxy = Proxy(port=PROXY_PORT)
            proxy.stop_server()
            if "proxy_cem" in sticky:
                del sticky["proxy_cem"]
