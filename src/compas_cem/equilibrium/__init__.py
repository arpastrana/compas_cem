"""
compas_cem.equilibrium
****************************

.. currentmodule:: compas_cem.equilibrium


Equilibrium
============

.. autosummary::
    :toctree: generated/
    :nosignatures:

    static_equilibrium
    static_equilibrium_numpy

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# from .<module> import *
from .force import *  # noqa F403

import compas
if not compas.IPY:
    from .force_numpy import *  # noqa F403

__all__ = [name for name in dir() if not name.startswith('_')]
