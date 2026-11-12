"""
The combinatorial equilibrium method for COMPAS.
"""

from __future__ import print_function

import os

__author__ = ["Rafael Pastrana"]
__copyright__ = "Rafael Pastrana"
__license__ = "MIT License"
__email__ = "arpj@princeton.edu"
__version__ = "0.9.1"


# Directories
HERE = os.path.dirname(__file__)
HOME = os.path.abspath(os.path.join(HERE, "../../"))
DATA = os.path.abspath(os.path.join(HOME, "data"))
DOCS = os.path.abspath(os.path.join(HOME, "docs"))
TEMP = os.path.abspath(os.path.join(HOME, "temp"))
JSON_DATA = os.path.abspath(os.path.join(DATA, "json"))

# RGB color scheme
COLORS = {
    "tension": (227, 6, 75),  # red
    "compression": (12, 119, 184),  # blue
    "edge": (50, 50, 50),  # dark gray
    "node": (255, 255, 255),  # white
    "node_black": (0, 0, 0),  # black
    "node_support": (0, 150, 10),  # green
    "node_origin": (155, 100, 255),  # purple
    "edge_trail": (180, 0, 255),  # purple
    "edge_deviation": (127, 255, 0),  # lime  (127, 155, 0)
    "edge_deviation_indirect": (255, 100, 47),  # coral
    "support_force": (75, 75, 75),  # dark gray
    "load": (0, 150, 10),  # green
    "trail": (250, 80, 210),  # pink
    "auxiliary_trail": (255, 155, 15),  # orange
}

# Arrow proportions as fractions of the arrow length, as jax_fdm draws them in 3D
ARROW_HEADPORTION = 0.12
ARROW_HEADWIDTH = 0.04
ARROW_BODYWIDTH = 0.012
# The 2D proportions of jax_fdm's plotter; widths are full widths, as matplotlib takes
ARROW_HEADPORTION_2D = 0.2
ARROW_HEADWIDTH_2D = 0.08
ARROW_BODYWIDTH_2D = 0.024
# The reach of a load cross from its node, as a fraction of the diagram's bounding-box diagonal
LOAD_CROSS_SIZE = 0.02

# TODO: add static equilibrium plugin
# The plotter, viewer and Grasshopper scene objects register themselves when
# their package is imported, so no plugin module is declared here.

__all__ = [
    "HOME",
    "DATA",
    "DOCS",
    "TEMP",
    "JSON_DATA",
    "COLORS",
    "ARROW_HEADPORTION",
    "ARROW_HEADWIDTH",
    "ARROW_BODYWIDTH",
    "ARROW_HEADPORTION_2D",
    "ARROW_HEADWIDTH_2D",
    "ARROW_BODYWIDTH_2D",
    "LOAD_CROSS_SIZE",
]
