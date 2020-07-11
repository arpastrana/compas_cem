"""
compas_cem.loads
****************************

.. currentmodule:: compas_cem.loads


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
from .point_load import *
from .self_weight import *

__all__ = [name for name in dir() if not name.startswith('_')]
