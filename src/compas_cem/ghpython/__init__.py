"""
Grasshopper components and scene objects that draw diagrams inside Rhino.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import compas

from .form_display import *  # noqa F403

# The scene objects and the preview import Rhino, which is importable inside
# Rhino only, so both the imports and the registration are guarded.
if compas.is_grasshopper():
    from compas.scene.context import register_scene_objects

    from .form_preview import *  # noqa F403
    from .scene_objects import *  # noqa F403
    from .scene_objects import register_ghpython_scene_objects

    # Built-in discovery must run first: compas only auto-discovers scene
    # objects into an empty registry, and it scans compas* packages only.
    register_scene_objects()
    register_ghpython_scene_objects()

__all__ = [name for name in dir() if not name.startswith("_")]
