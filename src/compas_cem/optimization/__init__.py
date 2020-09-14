"""
compas_cem.optimization
****************************

.. currentmodule:: compas_cem.optimization


Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:


Functions
=========

.. autosummary::
    :toctree: generated/
    :nosignatures:

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# from .<module> import *
from ._serialization import *
from .constraint import *
from .goals import *
from .proxy import *

import compas
if not compas.IPY:
    from ._nlopt import *
    from .objective_func import *
    from .grad import *
    from .optimizer import *

__all__ = [name for name in dir() if not name.startswith('_')]
