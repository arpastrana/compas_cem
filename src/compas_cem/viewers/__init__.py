"""
Three-dimensional viewing of topology and form diagrams.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

try:
    import compas_viewer as _compas_viewer  # noqa F401
except ImportError as error:
    message = "compas_cem.viewers needs the viz extra: pip install 'compas-cem[viz]'"
    raise ImportError(message) from error

from compas.scene.context import register_scene_objects

from .viewer import *  # noqa F403
from .scene_objects import *  # noqa F403
from .scene_objects import register_viewer_scene_objects

# Built-in discovery must run first: compas only auto-discovers scene objects
# into an empty registry, and it scans compas* packages only.
register_scene_objects()
register_viewer_scene_objects()

__all__ = [name for name in dir() if not name.startswith("_")]
