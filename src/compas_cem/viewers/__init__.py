"""
compas_cem.viewers
****************************

.. currentmodule:: compas_cem.viewers


Visualization objects
=====================

.. autosummary::
    :toctree: generated/
    :nosignatures:

    DiagramObject
    FormDiagramObject
    TopologyDiagramObject

Viewers
=======

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Viewer
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def is_compasviewers_installed():
    try:
        import compas_view2  # noqa F401
    except ImportError:
        return False
    return True


if is_compasviewers_installed():

    from .diagramobject import *  # noqa F403
    from .topologyobject import *  # noqa F403
    from .formobject import *  # noqa F403
    from .register import register_objects
    from .viewer import *  # noqa F403

    register_objects()


__all__ = [name for name in dir() if not name.startswith('_')]
