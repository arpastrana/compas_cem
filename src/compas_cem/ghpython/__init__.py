"""
compas_cem.ghpython
****************************

.. currentmodule:: compas_cem.ghpython


Artists
========

In **COMPAS CEM**, the `artists` are classes that assist with the visualization
of diagrams, in a way that maintains the data separated from the specific CAD
interfaces, while providing a way to leverage native performance of the CAD
environment.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    TopologyArtist
    FormArtist
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import compas

if compas.RHINO:
    from .artists import *  # noqa F403

__all__ = [name for name in dir() if not name.startswith('_')]
