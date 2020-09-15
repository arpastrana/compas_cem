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
import sys


__author__ = ["Rafael Pastrana" ]
__copyright__ = "Copyright 2020 - Princeton University"
__license__ = "MIT License"
__email__ = "arpj@princeton.edu"
__version__ = "0.1"


HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.abspath(os.path.join(HOME, "data"))
DOCS = os.path.abspath(os.path.join(HOME, "docs"))
TEMP = os.path.abspath(os.path.join(HOME, "temp"))
JSON_DATA = os.path.abspath(os.path.join(DATA, "json"))


__all__ = ["HOME", "DATA", "DOCS", "TEMP"]
