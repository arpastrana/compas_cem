"""
compas_cem.plotters
****************************

.. currentmodule:: compas_cem.plotters


Classes
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    FormPlotter
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# from .<module> import *
import compas

if not compas.IPY:
    from .formartist import *  # noqa F403
    from .topologyartist import *  # noqa F403

# from .proxy import *  # noqa F403

__all__ = [name for name in dir() if not name.startswith('_')]
