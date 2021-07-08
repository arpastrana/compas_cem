"""
compas_cem.optimization
****************************

.. currentmodule:: compas_cem.optimization.constraints


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
from .constraint import *  # noqa F403
from .point import *  # noqa F403
from .plane import *  # noqa F403
from .line import *  # noqa F403
from .force import *  # noqa F403
from .length import *  # noqa F403

# import compas
# if not compas.IPY:
#     from .mesh import *

__all__ = [name for name in dir() if not name.startswith('_')]
