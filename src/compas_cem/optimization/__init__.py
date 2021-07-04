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

Constraints
===========

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

NLOpt
=====
.. autosummary::
    :toctree: generated/
    :nosignatures:

    nlopt_algorithm
    nlopt_algorithms
    nlopt_solver    

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# from .<module> import *
from ._serialization import *
from .constraints import *
from .parameters import *
from .proxy import *

import compas
if not compas.IPY:
    from .nlopt import *
    from .objective_func import *
    from .grad import *
    from .optimizer import *


__all__ = [name for name in dir() if not name.startswith('_')]
