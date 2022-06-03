"""
********************************************************************************
compas_cem
********************************************************************************

.. currentmodule:: compas_cem


.. toctree::
    :maxdepth: 1

    compas_cem.diagrams
    compas_cem.elements
    compas_cem.loads
    compas_cem.supports
    compas_cem.equilibrium
    compas_cem.optimization
    compas_cem.plotters
    compas_cem.viewers
"""

from __future__ import print_function

import os

__author__ = ["Rafael Pastrana"]
__copyright__ = "Copyright 2020 - Princeton University"
__license__ = "MIT License"
__email__ = "arpj@princeton.edu"
__version__ = "0.5.0"


# Directories
HERE = os.path.dirname(__file__)
HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.abspath(os.path.join(HOME, "data"))
DOCS = os.path.abspath(os.path.join(HOME, "docs"))
TEMP = os.path.abspath(os.path.join(HOME, "temp"))
JSON_DATA = os.path.abspath(os.path.join(DATA, "json"))

# RGB color scheme
COLORS = {"tension": (227, 6, 75),  # red
          "compression": (12, 119, 184),  # blue
          "edge": (50, 50, 50),  # dark gray
          "node": (255, 255, 255),  # white
          "node_black": (0, 0, 0),  # black
          "node_support": (0, 150, 10),  # green
          "node_origin": (155, 100, 255),  # purple
          "edge_trail": (127, 0, 127),  # purple
          "edge_deviation": (127, 255, 0),  # lime
          "support_force": (75, 75, 75),  # dark gray / green (0, 150, 10)
          "load": (0, 150, 10),  # green / light green (50, 250, 100)
          "trail": (250, 80, 210),  # pink
          "auxiliary_trail": (255, 155, 15)}  # orange

PROXY_PORT = 7123

# TODO: add static equilibrium plugin
__all_plugins__ = ['compas_cem.ghpython.install',
                   'compas_cem.ghpython.uninstall',
                   'compas_cem.ghpython.register',
                   'compas_cem.plotters.register']

__all__ = ["HOME", "DATA", "DOCS", "TEMP", "JSON_DATA", "COLORS"]
