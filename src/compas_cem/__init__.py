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
"""

from __future__ import print_function

import os

__author__ = ["Rafael Pastrana"]
__copyright__ = "Copyright 2020 - Princeton University"
__license__ = "MIT License"
__email__ = "arpj@princeton.edu"
__version__ = "0.1.5"


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
          "node": (255, 255, 255),  # green
          "node_support": (0, 150, 10),  # green
          "node_origin": (155, 100, 255),  # purple
          "load": (0, 150, 10),  # green
          "support_force": (0, 150, 10),  # green
          "trail": (250, 80, 210),  # pink
          "auxiliary_trail": (255, 155, 15)  # orange
          }

__all_plugins__ = ['compas_cem.rhino_install']
__all__ = ["HOME", "DATA", "DOCS", "TEMP", "JSON_DATA", "COLORS"]
