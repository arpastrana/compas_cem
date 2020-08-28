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
import compas
if not compas.IPY:
    from .pull import *
    from .loss import *
    from .objective_func import *
    from .grad import *
    from ._nlopt import *
    from .optimizer import *

from .constraint import *
from .goal import *
from .proxy import *

__all__ = [name for name in dir() if not name.startswith('_')]
