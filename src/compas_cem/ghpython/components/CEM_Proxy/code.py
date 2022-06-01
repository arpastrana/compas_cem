"""
Create an RPC proxy server to solve a constrained form-finding problem via CPython
"""
from ghpythonlib.componentbase import executingcomponent as component

from scriptcontext import sticky

from compas.rpc import Proxy
from compas_cem import PROXY_PORT


class CEMProxyComponent(component):
    def RunScript(self, start, stop):

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
