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


__author__ = ['Patrick Ole Ohlbrock','Pierluigi D''Acunto' ]
__copyright__ = 'Copyright 2019 - Chair of Structural Design, ETH Zurich'
__license__ = 'MIT License'
__email__ = 'ohlbrock@arch.ethz.ch'
__version__ = "1.80"


HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.abspath(os.path.join(HOME, "data"))
DOCS = os.path.abspath(os.path.join(HOME, "docs"))
TEMP = os.path.abspath(os.path.join(HOME, "temp"))


__all__ = ["HOME", "DATA", "DOCS", "TEMP"]
