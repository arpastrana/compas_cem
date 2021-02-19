"""
compas_cem.optimization
****************************

.. currentmodule:: compas_cem.optimization


Optimization
============

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Optimizer
    optimizer_solve_nlopt_proxy
    solve_nlopt_proxy

Goals
=====

.. autosummary::
    :toctree: generated/
    :nosignatures:

    PointGoal
    LineGoal
    PlaneGoal
    TrimeshGoal
    NodeResidualGoal

Constraints
===========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    TrailEdgeConstraint
    DeviationEdgeConstraint


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
from .goals import *
from .proxy import *

import compas
if not compas.IPY:
    from .nlopt import *
    from .objective_func import *
    from .grad import *
    from .optimizer import *

    import jax
    # Global flag to set a specific platform, must be used at startup.
    jax.config.update('jax_platform_name', 'cpu')


__all__ = [name for name in dir() if not name.startswith('_')]
