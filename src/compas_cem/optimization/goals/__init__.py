"""
compas_cem.optimization
****************************

.. currentmodule:: compas_cem.optimization.goals


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
from .goal import *
from .point import *
from .plane import *
from .vector import *

import compas
if not compas.IPY:
    from .mesh import *

__all__ = [name for name in dir() if not name.startswith('_')]
