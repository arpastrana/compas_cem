"""
compas_cem.optimization
****************************

.. currentmodule:: compas_cem.optimization

Optimizers
==========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Optimizer
    solve_nlopt_proxy

Optimization Constraints
========================

.. autosummary::
    :toctree: generated/
    :nosignatures:

    PointConstraint
    LineConstraint
    PlaneConstraint
    DeviationEdgeLengthConstraint
    TrailEdgeForceConstraint
    ReactionForceConstraint

Optimization Parameters
=======================

.. autosummary::
    :toctree: generated/
    :nosignatures:

    TrailEdgeParameter
    DeviationEdgeParameter
    OriginNodeXParameter
    OriginNodeYParameter
    OriginNodeZParameter
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# from .<module> import *
from .constraints import *  # noqa F403
from .parameters import *  # noqa F403
from .proxy import *  # noqa F403

import compas
if not compas.IPY:
    from .nlopt import *  # noqa F403
    from .objective_func import *  # noqa F403
    from .grad import *  # noqa F403
    from .optimizer import *  # noqa F403


__all__ = [name for name in dir() if not name.startswith('_')]
