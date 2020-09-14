"""
********************************************************************************
compas_cem
********************************************************************************

.. currentmodule:: compas_cem


.. toctree::
    :maxdepth: 1


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
