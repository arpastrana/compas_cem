"""
The constrained form-finding solver, its goals and its optimization parameters.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


# from .<module> import *
from .goals import *  # noqa F403
from .parameters import *  # noqa F403
from .proxy import *  # noqa F403

import compas

if not compas.IPY:
    from .nlopt import *  # noqa F403
    from .objective_func import *  # noqa F403
    from .grad import *  # noqa F403
    from .optimizer import *  # noqa F403


__all__ = [name for name in dir() if not name.startswith("_")]
